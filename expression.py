from collections import defaultdict
from itertools import count

import re
from jinja2 import Template

TAG_RE = re.compile('\{\{\s*?(?P<tag>[a-zA-Z]\w*)\s*?\}\}')

def disambiguate(label, taken):
    if label not in taken:
        return label
    suffix = "_%2.2i"
    label = str(label)
    for i in count(1):
        candidate = label + (suffix % i)
        if candidate not in taken:
            return candidate

class Expression(object):
    """Representation of a python expression with variable dependencies

    Expression objects are defined by 3 attributes:

     * template: A string like "{{x}} + 5"
     * an optional list of reference objects, like [x]
     * an optional output_ref reference, like y

     This example represents the statement "y = x + 5". The names for
     the inputs and outputs are not directly specified in the
     template, but are rather chosen by an ExpressionManager to avoid
     name conflicts
    """
    def __init__(self, template=None, inlined=False, out_name_hint = None,
                 **kwargs):
        self.template = template
        if 'output_ref' in kwargs:
            self.output_ref = kwargs.pop('output_ref')
        self.refs = kwargs
        self.inlined = inlined
        self.out_name_hint = out_name_hint

    def render(self, oracle):
        """Render self into python expression

        :param oracle: A class with a get_reference() method. Takes a
        python object as input, returns python string to describe that

        :rtype: String: a valid python statement of the expression
        """
        t = Template(self.template)
        tags = TAG_RE.findall(self.template)
        kwargs = dict((tag, oracle.reference(self.refs[tag])) for tag in tags)
        result = str(t.render(**kwargs))
        return result

    @property
    def dependencies(self):
        """List of distinct objects that this expression depends on

        Raises RuntimeError if template is not defined, or if dependencies
        are missing
        """
        if self.template is None:
            raise RuntimeError("Expression crated without a template")

        tags = TAG_RE.findall(self.template)
        result = []
        for t in tags:
            if t in result:
                continue
            if t not in self.refs:
                raise RuntimeError("Missing dependency for %s" % t)
            result.append(self.refs[t])
        return result

    def __lt__(self, other):
        if not hasattr(self, 'output_ref'):
            return False
        for dep in other.dependencies:
            if dep is self.output_ref:
                return True
        return False


class ExpressionGroup(object):
    """Collection of expressions that should be executed together, in order"""
    def __init__(self, expressions=None):
        self.expressions = expressions or []

    @property
    def dependencies(self):
        result =[]
        for e in self.expressions:
            for dep in e.dependencies:
                if dep not in result:
                    result.append(dep)
        return result

    def render(self, oracle):
        return [e.render(oracle) for e in self.expressions]


class ExpressionManager(object):
    def __init__(self, exps=None):
        self._exps = []
        self._refs = {}
        self._ref_labels = {}
        if exps is not None:
            self.extend(exps)

    def ordered_expressions(self):
        return sorted(self._exps)

    def _register_reference_label(self, obj, hint=''):
        hint = hint or 'object'
        oid = id(obj)
        assert oid not in self._ref_labels
        name = disambiguate(hint, set(self._ref_labels.values()))
        self._ref_labels[oid] = name

    def reference(self, obj):
        """A variable name for an object, or definition if inlined """

        oid = id(obj)

        if oid not in self._ref_labels or oid not in self._refs:
            raise KeyError("Object with id %i not registered with "
                           "manager: %r" % (oid, self._ref_labels))

        exp = self._refs[oid]
        if exp.inlined:
            return self.definition(obj)
        else:
            return self._ref_labels[oid]

    def definition(self, obj):
        """Code that defines an object"""
        oid =id(obj)
        if oid not in self._refs:
            raise KeyError("No expression that defines %r" % obj)

        exp = self._refs[oid]
        return exp.render(self)

    def extend(self, expressions):
        for e in expressions:
            self.append(e)

    def append(self, expression):
        if expression in self._exps:
            return

        self._exps.append(expression)
        if not hasattr(expression, 'output_ref'):
            return

        out = expression.output_ref
        oid = id(out)
        if oid in self._refs:
            raise RuntimeError("Conflicting expressions to define %r" % out)

        self._refs[oid] = expression
        self._register_reference_label(out, hint=expression.out_name_hint)
