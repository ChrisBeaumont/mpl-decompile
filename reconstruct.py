from matplotlib.lines import Line2D
from matplotlib.collections import PathCollection

import numpy as np

from properties import plot_properties, scatter_properties

def _set_properties(variable, reference, properties):
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


def reconstruct_array(array, variable='x'):
    """ Reconstruct a numpy array """
    array = np.asarray(array)
    dtype = array.dtype
    string = array.tostring()
    result = '%s = np.fromstring(%r, dtype=np.%s)' % (variable, string,
                                                      dtype)
    if len(array.shape) != 1:
        result += '\n%s.shape = %r' % (variable, array.shape)
    return result

def reconstruct_plot(artist, variable='artist'):
    """ Reconstruct a matplotlib.lines.Line2D object into a plot call"""

    if not isinstance(artist, Line2D):
        raise TypeError("Input must be a Line2D object")

    x = artist.get_xdata()
    y = artist.get_ydata()

    result = []
    result.append(reconstruct_array(x, 'x'))
    result.append(reconstruct_array(y, 'y'))
    result.append('%s, = plt.plot(x, y)' % variable)
    result.extend(_set_properties(variable, artist, plot_properties))
    return '\n'.join(result)


def reconstruct_scatter(artist, variable='artist'):
    """ Reconstruct a PathCollection as a call to plt.scatter """
    if not isinstance(artist, PathCollection):
        raise TypeError("Input must be a PathCollection")

    xy = artist.get_offsets()

    result = []
    result.append(reconstruct_array(xy, 'xy'))
    result.append('%s = plt.scatter(xy[:, 0], xy[:, 1])' % variable)
    result.extend(_set_properties(variable, artist, scatter_properties))
    return '\n'.join(result)

def main():
    import matplotlib.pyplot as plt
    print 'import matplotlib.pyplot as plt'
    print 'from numpy import *'
    print 'import numpy as np'
    x = plt.scatter([2,3,4,1,3,2], [2,1,2,1,1,1])
    print reconstruct_scatter(x)
    print 'plt.show()'

if __name__ == "__main__":
    main()
