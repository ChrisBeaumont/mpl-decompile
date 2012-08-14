""" Example use of the Decompiler

Try running this script like
python demo.py > out.py
python out.py

ISSUES:
-------
Axes limits are not being set correctly?
"""
import matplotlib.pyplot as plt
from decompiler import Decompiler

p, = plt.plot([1,2,3], [2,3,4], 'ro-', alpha = .3, markerfacecolor='b')
p.axes.set_xlim(-2, 20)
p.axes.set_ylim(-50, 50)
d = Decompiler()
d.ingest(p.figure)
print d.render()
print 'plt.show()'
