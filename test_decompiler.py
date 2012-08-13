from expression import Expression
from decompiler import Decompiler

import pytest

def _test_equality(s, ref, x):
    exec(s)
    assert locals()[ref] == x

ATOMS = (0, 0., 0L, 0j, True, False, '0', u'0', None)

@pytest.mark.parametrize(('arg'), ATOMS)
def test_dict_decompile(arg):
    d = Decompiler()
    x = dict([('b', arg), ('a', arg)])
    d.ingest(x)
    ref = d.mgr.reference(x)
    result = "%s = { 'a': %r, 'b': %r }" % (ref, arg, arg)

    assert d.render() == result
    _test_equality(d.render(), ref, x)

def test_inline_list_decompile():
    d = Decompiler()
    x = [1, 1, 2., 3j, False, 3L, '3', u'3']
    d.ingest(x)
    ref = d.mgr.reference(x)
    result = "%s = %r" % (ref, x)
    assert d.render() == result
    _test_equality(d.render(), ref, x)

def test_inline_tuple_decompile():
    d = Decompiler()
    x = (1, 1, 2., 3j, False, 3L, '3', u'3')
    d.ingest(x)
    ref = d.mgr.reference(x)
    result = "%s = %r" % (ref, x)

    assert d.render() == result
    _test_equality(d.render(), ref, x)

def test_add_import():
    d = Decompiler()
    d.add_import('import numpy as np')
    assert d.render() == 'import numpy as np'

def test_repeated_add_import():
    """Don't repeat import statements on render"""
    d = Decompiler()
    d.add_import('import numpy as np')
    d.add_import('import numpy as np')
    assert d.render() == 'import numpy as np'

def test_numpy_decompile():
    import numpy as np
    x = np.array([1,2,3,4])
    s = x.dumps()
    d = Decompiler()
    d.ingest(x)

    ref = d.mgr.reference(x)
    answer = "import numpy as np\n%s = np.loads(%r)" % (ref, s)

    assert d.render() == answer
    exec(d.render())
    np.testing.assert_array_equal(locals()[ref],  x)

def test_unsupported_type():
    """Raise type error when trying to ingest an unsupported type"""
    class Foo(object):
        pass
    d = Decompiler()

    with pytest.raises(TypeError) as exc:
        d.ingest(Foo())
    assert exc.value.args[0] == ("Don't know how to decompile objects of "
                                 "type %s" % type(Foo()))

def test_name_hint():
    """In the absence of name conflicts, output ref should use name_hint"""
    x = [5]
    d = Decompiler()
    d.ingest(x, name_hint='zzz')

    answer = "zzz = [5]"
    result = d.render()

    assert answer == result

def test_magic_method():
    """Decompiler looks for __expfac__ for expression factories"""
    class Foo(object):
        def __init__(self, x):
            self.x = x

        def __expfac__(self, decompiler, obj):
            return [Expression("Foo({{x}})", x=obj.x, output_ref = obj)]

    f = Foo(4)
    d = Decompiler()
    d.ingest(f)

    ref = d.mgr.reference(f)
    answer = "%s = Foo(4)" % ref
    result = d.render()

    assert result == answer
