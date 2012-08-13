from itertools import count

from matplotlib.lines import Line2D
from matplotlib.collections import PathCollection
from matplotlib.image import AxesImage

import numpy as np

from properties import plot_properties, scatter_properties

def disambiguate(label, taken):
    if label not in taken:
        return label
    suffix = "_%2.2i"
    label = str(label)
    for i in count(1):
        candidate = label + (suffix % i)
        if candidate not in taken:
            return candidate


class Reconstructor(object):
    """ Top level class

    Intended usage:
    Reconstructor(figure_object).dump(file)

    writes a self-contained pythons script to file

    Note: The structure of this class follows that of pickle.Pickler
    """
    dispatch = {}

    def __init__(self, obj):
        self._statements = []
        self._variables = []
        self._taken = set()
        self._reconstruct(obj)

    def _add_statements(self, statements):
        """Used to register new python statements to the script.
        These will be output in the order that they were registered"""
        if type(statements) == list:
            self._statements.extend(statements)
        else:
            assert type(statements) == str
            self._statements.append(statements)

    def _import_statements(self):
        return "import matplotlib.pyplot as plt\nimport numpy as np"

    def _variable_statements(self):
        return '\n'.join(self._variables)

    def _plot_statements(self):
        return '\n'.join(self._statements)

    def _reconstruct(self, obj, **kwargs):
        """ Calculate and store commands that reconstruct obj.

        Returns the variable name of the reconstructed object
        """
        if type(obj) in self.dispatch:
            return self.dispatch[type(obj)](self, obj, **kwargs)
        else:
            raise TypeError("Cannot reconstruct object of type %s: %s" %
                            (type(obj), obj))

    def _register_variable(self, target_name, definition):
        """ Let's other dispatchers define variables.

        These get defined together in the output script. The goal is
        to produce cleaner syntax, so that instead of::

            plt.plot(<long numpy array definition)

        the output looks like::

            x = <long numpy array definiton>
            <other variable definitions>

            plt.plot(x)

        The registry will also disambiguate variable names to avoid
        name conflicts

        :param target name: The desired variable name (may change)
        :param definition: python command to define the variable

        :rtype: string -- the variable name that was actually used
        (may be changed to avoid name collisions)

        *Example*

        >>> _register_variable('x', 'np.array([1,2,3,4,5])')
        x_01  # name has been disambiguated
        """
        target_name = disambiguate(target_name, self._taken)
        self._variables.append("%s = %s" % (target_name, definition))
        self._taken.add(target_name)
        return target_name

    def dump(self, outfile):
        """ Write script to result file """

        outfile.write(self._import_statements())
        outfile.write('\n\n# variable statements\n')
        outfile.write(self._variable_statements())
        outfile.write('\n\n# plot statements\n')
        outfile.write(self._plot_statements())

    def dumps(self):
        """ Return script as a string """
        from StringIO import StringIO
        obj = StringIO()
        self.dump(obj)
        return obj.getvalue()

    def reconstruct_array(self, array, varname='arr'):
        """ Reconstruct a numpy array """
        array = np.asarray(array)
        dtype = array.dtype
        string = array.tostring()
        shape = array.shape

        defn = 'np.fromstring(%r, dtype=np.%s)' % (string, dtype)
        var = self._register_variable(varname, defn)
        if len(shape) != 1:
            self._add_statements('%s.shape = %r' % (var, shape))
        return var

    dispatch[np.ndarray] = reconstruct_array

    def reconstruct_plot(self, artist, varname='artist'):
        """ Reconstruct a matplotlib.lines.Line2D object into a plot call"""
        assert isinstance(artist, Line2D)

        x = artist.get_xdata()
        y = artist.get_ydata()
        vx = self._reconstruct(x)
        vy = self._reconstruct(y)

        result = ['%s, = plt.plot(%s, %s)' % (varname, vx, vy)]
        result.extend(_set_properties(varname, artist, plot_properties))
        self._add_statements(result)
        return varname

    dispatch[Line2D] = reconstruct_plot

    def reconstruct_scatter(self, artist, varname='artist'):
        """ Reconstruct a PathCollection as a call to plt.scatter """
        assert isinstance(artist, PathCollection)

        xy = artist.get_offsets()
        xy = self._reconstruct(xy)

        result = []
        result.append('%s = plt.scatter(%s[:, 0], %s[:, 1])' %
                      (varname, xy, xy))
        result.extend(_set_properties(varname, artist, scatter_properties))
        self._add_statements(result)
        return varname

    def reconstruct_image(self, artist, varname='artist'):
        assert isinstance(artist, AxesImage)

    dispatch[PathCollection] = reconstruct_scatter
    #XXX add lots more dispatch methods!

Sfeferein
def _set_properties(variable, reference, properties):
    """ Create commands like variable.set_property(value), to sync to
    properties of reference artist"""

    #XXX some properties are objects like array, that need
    #to be properly decompiled. It would be best if short definitions
    #were defined inline, while longer ones were registered as variables
    result = []
    for prop, default in properties:
        val = getattr(reference, 'get_%s' % prop)()
        try:
            if val == default:
                continue
        except ValueError:
            pass
        result.append('%s.set_%s(%r)' % (variable, prop, val))
    return result


def main():
    """ Try piping this into python """
    import matplotlib.pyplot as plt
    x, = plt.plot([1,4,3,1], 'r--', alpha=.3)
    print Reconstructor(x).dumps()
    print 'plt.show()'

if __name__ == "__main__":
    main()



"""
General approach

take an object
unpack its contents
recursively handle its contents

reconstruct current object
 -- need references to other objects -- ask a registry
 -- may be variables, or inlined

Idea -- build a reconstruction tree, representing basic syntax and
data references. Separate function turns into code

Concept Inventory
-----------------
Data registry -- oracle that accepts objects, returns variable name and/or code defn

Atomic decompiler -- object-specific object for single entity

Code Tree (Network?) representation of instructions to execute, encodes dependencies

decompiler -- turns code tree into code string

statement -- way to specify a line of code, and flexiby specify variable dependency. Link to object, not to name (let decompiler deal with that)

plt.plot( {{xvar}}, {{yvar}})
xvar -> python object
yvar -> python object
output -> None or target created object

{{object}}.axes.set_xlimit({{x}})
object -> artist object
x -> list object


How does decompiler work?
Builds dependency graph for all creation statements
Topological sort to determine what order things must be defined in
Uses atomic decompilers to generate statements. Decides whether to inline based on reference count & defn length
Uses variable registry to get unique variable names for everything
Prints out in order

(optional): uses HDF5 to create a data file, so big arrays not output as intimidating pythong code

"""


