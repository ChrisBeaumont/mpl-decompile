from expression import (Expression, ExpressionGroup,
                        ExpressionManager)

import pytest

class SimpleOracle(object):
    def reference(self, x):
        return str(x)

def test_expression_nosub():
    e = Expression("Hello there")

    assert e.render(SimpleOracle()) == "Hello there"

def test_expression_onesub():
    e = Expression()
    e.template = "Hello {{person}}"
    e.refs['person'] = 5

    assert e.render(SimpleOracle()) == "Hello 5"

def test_expression_twosub():
    e = Expression("Hello {{person}}! I am {{me}}", person=5, me=6)

    assert e.render(SimpleOracle()) == "Hello 5! I am 6"

def test_expression_unused_sub():
    e = Expression("Hello {{person}}!", person=5, me=6)

    assert e.render(SimpleOracle()) == "Hello 5!"

def test_dependencies():
    e = Expression("Hello {{person}}", person=5, me=6)

    assert set(e.dependencies) == set([5])

def test_dependency_without_template():
    """should raise a RuntimeError"""
    with pytest.raises(RuntimeError) as r:
        e = Expression()
        e.dependencies

def test_dependency_with_missing_item():
    with pytest.raises(RuntimeError) as r:
        e = Expression("{{hi}}")
        e.dependencies

def test_expression_group_dependencies():
    e = Expression()
    e.template = "Hello {{person}}!"
    e.refs['person'] = 5
    e2 = Expression()
    e2.template = "I am {{person}}"
    e2.refs['person'] = 6
    eg = ExpressionGroup([e, e2])
    assert set(eg.dependencies) == set([5, 6])

def test_expression_group_render():
    e1 = Expression("{{hi}}", hi=1)
    e2 = Expression("my name is {{me}}", me="chris")
    eg = ExpressionGroup([e1, e2])
    assert eg.render(SimpleOracle()) == ['1', 'my name is chris']

def test_unhashable_dependency():
    """Even unhashable dependencies should be processable"""
    e = Expression("{{hi}}", hi=[1,2,3])
    assert e.dependencies[0] == [1,2,3]


def test_unregistered_reference():
    """Trying to reference unregistered object raises KeyError"""
    em = ExpressionManager()
    with pytest.raises(KeyError) as exc:
        em.reference(3)
    assert exc.value.args[0].startswith("Object with id")

def test_unregistered_definition():
    """Trying to define unregistered object raises KeyError"""
    em = ExpressionManager()
    with pytest.raises(KeyError) as exc:
        em.definition(3)
    assert exc.value.args[0] == "No expression that defines 3"

def test_expmgr_get_simple_reference():
    x = (1,2,3)
    em = ExpressionManager()
    e = Expression("(1, 2, 3)", hi=5, output_ref=x)
    em.append(e)
    assert em.definition(x) == '(1, 2, 3)'

def test_expmgr_get_templated_reference():
    x = [1,2,3]
    y = [2,3,4]
    e = Expression("[_ + 1 for _ in {{x}}]", x=x, output_ref=y)
    e2 = Expression("[1, 2, 3]", output_ref=x)
    em = ExpressionManager()
    em.extend([e2, e])

    varx = em.reference(x)
    assert em.definition(y) == ("[_ + 1 for _ in %s]" % varx)

def test_expmgr_reference_inlined():
    """Should return definition if inlined"""
    x = [1,2,3]
    e = Expression("[1,2,3]", output_ref=x, inlined=True)
    em = ExpressionManager()
    em.append(e)
    assert em.reference(x) == "[1,2,3]"

def test_expmgr_assigns_unique_references():
    x = [1,2,3]
    y = [2,3,4]
    e1 = Expression("[1, 2, 3]", output_ref=x)
    e2 = Expression("[2, 3, 4]", output_ref=y)
    em = ExpressionManager([e1, e2])
    assert em.reference(x) != em.reference(y)

def test_conflicting_definitions():
    em = ExpressionManager()
    x=5
    e1 = Expression("5", output_ref=x)
    e2 = Expression("5L", output_ref=x)
    with pytest.raises(RuntimeError) as exc:
        em.extend([e1, e2])
    assert exc.value.args[0] == "Conflicting expressions to define 5"

def test_double_append():
    """Objects should be double appendable without catastrophe"""
    em = ExpressionManager()
    e1 = Expression("5")
    em.append(e1)
    em.append(e1)

def test_expression_compare():
    x = 5
    y = 8
    e1 = Expression("{{x}} + 3", x=x, output_ref = y)
    e2 = Expression("{{5}}", output_ref = x)
    assert e2 < e1

def test_dependency_graph():
    x, y, z = 5, 6, 11
    e1 = Expression("5", output_ref = x)
    e2 = Expression("{{x}} + 1", output_ref = y, x=x)
    e3 = Expression("{{x}} + {{y}}", output_ref=z, x=x, y=y)

    depgraph = {e1 : set(),
                e2 : set([e1]),
                e3 : set([e1, e2])}

    em = ExpressionManager()
    em.extend([e1, e2, e3])
    assert em.dependency_graph() == depgraph

def test_ordered_expressions():
    x, y, z = 5, 6, 11
    e1 = Expression("5", output_ref = x)
    e2 = Expression("{{x}} + 1", output_ref = y, x=x)
    e3 = Expression("{{x}} + {{y}}", output_ref=z, x=x, y=y)

    em = ExpressionManager()
    em.extend([e1, e3, e2])

    assert em.ordered_expressions() == [e1, e2, e3]
