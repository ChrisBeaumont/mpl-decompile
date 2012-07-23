=====================
Matploblib Decompiler
=====================

This is an experimental repository to explore how feasible it is to
"decompile" matplotlib objects back into sensible lines of Python commands
that re-generate them

The main issue is that most people create matplotlib plots with commands
like scatter([1,2,3], [2,3,4]). However, these commands are factory methods
which produce lots of low-level artists like Line2D, Spine, Text, etc.

The gloal is to develop a magical interface like this:


    >>> artist = plt.scatter([1,2,3], [2,3,4], alpha = .3)
    >>> print, decompile(artist)
    x = np.array([1,2,3])
    y = np.array([2,3,4])
    artist = plt.scatter(x, y)
    artist.set_alpha(0.3)

Such functionality would allow people to interact with figures using
GUI tools, and then export figures into reproducible, tweakable scripts

For a (barely) working example, see the ``main()`` method in ``reconstruct.py``