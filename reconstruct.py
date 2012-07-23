from matplotlib.lines import Line2D
import numpy as np

def reconstruct_array(array, variable='x'):
    array = np.asarray(array)
    dtype = array.dtype
    string = array.tostring()
    result = '%s = np.fromstring(%r, dtype=np.%s)' % (variable, string,
                                                      dtype)
    return result

def reconstruct_plot(artist):
    """ Reconstruct a matplotlib.lines.Line2D object into a plot call"""

    if not isinstance(artist, Line2D):
        raise TypeError("Input must be a Line2D object")

    x = artist.get_xdata()
    y = artist.get_ydata()

    result = []
    result.append(reconstruct_array(x, 'x'))
    result.append(reconstruct_array(y, 'y'))
    result.append('artist, = plt.plot(x, y)')

    properties = ('alpha color marker markeredgecolor markeredgewidth '
                  'markerfacecolor markerfacecoloralt '
                  'markersize visible ').split()
    for p in properties:
        val = getattr(artist, 'get_%s' % p)()
        result.append('artist.set(%s=%s)' % (p, repr(val)))

    return '\n'.join(result)


