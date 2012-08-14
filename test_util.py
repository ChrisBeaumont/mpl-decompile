from util import toposort

import pytest

def test_toposort_simple():
    data = {'a' : set('b'),
            'b' : set()}
    assert toposort(data) == ['b', 'a']

def test_toposort_adds_orphan_vertices():
    data = {'a' : set('b')}
    assert toposort(data) == ['b', 'a']

def test_toposort_subsorts():
    """After dependency sorting, normal sorting used"""
    data = {'a' : set('cbfjq')}
    assert toposort(data) == ['b', 'c', 'f', 'j', 'q', 'a']

def test_error_on_cycle():
    data = {'a' : set('b'),
            'b' : set('a')}
    with pytest.raises(TypeError) as exc:
        toposort(data)
    assert exc.value.args[0].startswith('A cyclic dependency')

def test_ignore_self_dependencies():
    data = {'a' : set('ab')}
    assert toposort(data) == ['b', 'a']

def test_large_example():
    """Taken from http://code.activestate.com/recipes/577413-topological-sort/"""
    data = {
        'des_system_lib':   set('std synopsys std_cell_lib des_system_lib dw02 dw01 ramlib ieee'.split()),
        'dw01':             set('ieee dw01 dware gtech'.split()),
        'dw02':             set('ieee dw02 dware'.split()),
        'dw03':             set('std synopsys dware dw03 dw02 dw01 ieee gtech'.split()),
        'dw04':             set('dw04 ieee dw01 dware gtech'.split()),
        'dw05':             set('dw05 ieee dware'.split()),
        'dw06':             set('dw06 ieee dware'.split()),
        'dw07':             set('ieee dware'.split()),
        'dware':            set('ieee dware'.split()),
        'gtech':            set('ieee gtech'.split()),
        'ramlib':           set('std ieee'.split()),
        'std_cell_lib':     set('ieee std_cell_lib'.split()),
        'synopsys':         set(),
        }
    result = toposort(data)
    answer = ('ieee std synopsys dware gtech ramlib std_cell_lib '
              'dw01 dw02 dw05 dw06 dw07 des_system_lib dw03 dw04').split()
    assert result == answer

def test_not_set():
    """Error raised if values not sets"""
    data = {'a' : ['a', 'b']}
    with pytest.raises(TypeError) as exc:
        toposort(data)
    assert exc.value.args[0] == 'All values must be sets'

def test_not_dict():
    """ Error raised if data not a dist """
    with pytest.raises(TypeError) as exc:
        toposort('3')
    assert exc.value.args[0] == 'Data must be a dictionary of sets'

def test_empty_data():
    assert toposort({}) == []

def test_empty_dependency():
    assert toposort({'a':set()}) == ['a']
