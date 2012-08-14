=====================
Matplotlib Decompiler
=====================

This is an experimental repository to explore how feasible it is to
"decompile" matplotlib objects back into sensible lines of Python commands that re-generate them. Think of it as a Pickle module that ouputs python code.

The main issue is that most people create matplotlib plots with commands
like scatter([1,2,3], [2,3,4]). However, these commands are factory methods
which produce lots of low-level artists like Line2D, Spine, Text, etc.

The gloal is to develop a magical interface like this:

    >>> from decompiler import Decompiler
    >>> artist = plt.scatter([1,2,3], [2,3,4], alpha = .3)
    >>> d = Decompiler()
    >>> d.ingest(artist.figure)
    >>> print d.render()
    [code that recreates the figure]

Such functionality would allow people to interact with figures using
GUI tools, and then export figures into reproducible, tweakable scripts

For a (barely) working example, see ``demo.py``


Current Approach
----------------

Code that inspects python objects and generates a python script to
clone them needs to address the following issues:

 1) How to create a clone of an object with python code

 2) How to name variables to avoid name collisions in
 the output script

 3) How to order lines of code such that objects are re-created
 int he proper order

Issue 1 is addressed via factory methods that know how to recreate
specific types of python objects. The ``Decompiler`` class has several
factory methods for converting simple data types like floats, ints,
numpy arrays, and some matplotlib types. In addition, the
``Decompiler`` class looks to see if an object has an ``__expfac__``
method and, if so, uses this method as the factory method. More
details on what the factory methods do is explained below.

The ``Expression`` object addresses issues 2 and 3. ``Expression``
objects represent single python expressions, without directly
specifying variable names. For example, consider the statement:

    z = max(1, 2, y)

This is represented by the following Expression object:

    e = Expression("max(1, 2, {{y_var}}", output_ref=z, y_var=y)

``e`` serves as a description of how to recreate z. It specifies that
z depends on the object y, without explicitly defining what variable
name should be assigned to the recreated copy of y or z.

Factory methods return lists of Expression objects necessary to
recreate a particular object. The ``Decompiler`` collects all these
expressions, finds dependencies (and the expression factories for those objects), determines the order in which to execute everything, and assigns variable names.