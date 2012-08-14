import types

from expression import Expression, ExpressionManager


class Decompiler(object):
    """Builds expressions from objects, determines order of execution,
    use ExpressionManager to build script"""

    expression_factory = {}

    def __init__(self, manager = None):
        self.mgr = manager or ExpressionManager()
        self._processed = {}
        self._imports = []

    def ingest(self, obj, name_hint=None):
        """ Recursively decompile an object into Expression objects """
        oid = id(obj)
        if oid in self._processed:
            return

        typ = type(obj)
        try:
            func = obj.__expfac__
        except AttributeError:
            try:
                func = self.expression_factory[typ]
            except KeyError:
                raise TypeError("Don't know how to decompile objects "
                                "of type %s" % typ)

        exps = func(self, obj)
        if exps[0].output_ref is not obj:
            raise TypeError("First expression returned from expression factory"
                            " must define %r as output ref" % obj)
        if name_hint:
            exps[0].out_name_hint = name_hint

        deps = [d for e in exps for d in e.dependencies]
        self._processed[oid] = obj

        for d in deps:
            self.ingest(d)

        self.mgr.extend(exps)

    def add_import(self, stmt):
        if stmt not in self._imports:
            self._imports.append(stmt)

    def render(self):
        """Render all decompiled objects into python statements"""
        result = []
        result.extend(self._imports)
        for exp in self.mgr.ordered_expressions():
            if exp.inlined:
                continue

            if hasattr(exp, 'output_ref'):
                out = exp.output_ref
                result.append("%s = %s" % (self.mgr.reference(out),
                                          exp.render(self.mgr)))
            else:
                result.append(exp.render(self.mgr))

        return '\n'.join(result)

    def _literal_factory(self, x):
        e = Expression("%r" % x, output_ref=x, inlined=True)
        return [e]

    expression_factory[types.IntType] = _literal_factory
    expression_factory[types.LongType] = _literal_factory
    expression_factory[types.ComplexType] = _literal_factory
    expression_factory[types.BooleanType] = _literal_factory
    expression_factory[types.StringType] = _literal_factory
    expression_factory[types.FloatType] = _literal_factory
    expression_factory[types.UnicodeType] = _literal_factory
    expression_factory[types.UnicodeType] = _literal_factory
    expression_factory[types.NoneType] = _literal_factory

    def _item_fac(self, x, wrapper):
        num = len(x)
        template = ', '.join(["{{x_%3.3i}}" % i for i in range(num)])
        template = wrapper % template
        kwargs = {}
        do_inline = num <= 5
        for i in range(num):
            kwargs["x_%3.3i" % i] = x[i]
        return [Expression(template, output_ref = x, inlined=do_inline, **kwargs)]

    def _list_factory(self, x):
        return self._item_fac(x, '[%s]')

    expression_factory[types.ListType] = _list_factory

    def _tuple_factory(self, x):
        return self._item_fac(x, '(%s)')

    expression_factory[types.TupleType] = _tuple_factory

    def _dict_factory(self, x):
        num = len(x)
        template = ', '.join(["{{k_%3.3i}}: {{v_%3.3i}}" % (i,i)
                              for i in range(num)])
        template = "{ %s }" % template
        kwargs = {}
        items = sorted(x.items())
        for i in range(num):
            kwargs['k_%3.3i' % i] = items[i][0]
            kwargs['v_%3.3i' % i] = items[i][1]
        return [Expression(template, output_ref = x, **kwargs)]

    expression_factory[types.DictType] = _dict_factory

    def _ndarray_factory(self, x):
        self.add_import('import numpy as np')
        s = x.dumps()
        template = 'np.loads({{s}})'
        return [Expression(template, s=s, output_ref=x)]

    try:
        import numpy as np
        expression_factory[np.ndarray] = _ndarray_factory
        expression_factory[np.float64] = _literal_factory
    except ImportError:
        pass

    try:
        import matplotlib.pyplot as plt
        import matplotlib.cbook as cbook
        from matplotlib.lines import Line2D
        from matplotlib.collections import PathCollection
        from matplotlib.axes import Axes, _subplot_classes
        from matplotlib.figure import Figure
        import mpl_factories as mplf
        expression_factory[Line2D] = mplf.mpl_plot_fac
        expression_factory[PathCollection] = mplf.mpl_scatter_fac
        expression_factory[Axes] = mplf.mpl_axes_fac
        expression_factory[Figure] = mplf.mpl_figure_fac
        expression_factory[plt.Rectangle] = mplf.mpl_rect_fac
        expression_factory[cbook.silent_list] = _list_factory

        ### subclasses can be defined after this statement
        for subplt in _subplot_classes.values():
            expression_factory[subplt] = mplf.mpl_subplot_fac
    except ImportError:
        pass
