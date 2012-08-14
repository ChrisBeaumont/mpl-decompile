from properties import (plot_properties, scatter_properties,
                        axes_properties, figure_properties, rect_properties)

from expression import Expression

def _set_properties(artist, properties):
    result = []
    for prop in properties:
        val = getattr(artist, 'get_%s' % prop)()
        result.append(Expression("{{artist}}.set_%s( {{val}} )" % prop,
                                 artist=artist, val=val))
    return result

def mpl_plot_fac(decomp, artist):
    x = artist.get_xdata()
    y = artist.get_ydata()

    template = "{{ax}}.plot({{x}}, {{y}})[0]"
    exps = [Expression(template, x=x, y=y,
                       output_ref=artist,
                       ax = artist.axes,
                       out_name_hint="p")]
    exps.extend(_set_properties(artist, plot_properties))
    decomp.ingest(x, name_hint='x')
    decomp.ingest(y, name_hint='y')
    return exps

def mpl_scatter_fac(decomp, artist):
    decomp.add_import('import matplotlib.pyplot as plt')

    xy = artist.get_offsets()
    result = []

    result.append(Expression("plt.scatter({{xy}}[:, 0], {{xy}}[:, 1])",
                             xy=xy, output_ref=artist,
                             out_name_hint="scatter"))
    result.extend(_set_properties(artist, scatter_properties))
    return result

def mpl_axes_fac(decomp, ax):
    result = [Expression("{{fig}}.add_subplot(*{{geom}})",
                         output_ref = ax, fig=ax.figure,
                         geom = ax.get_geometry(),
                         out_name_hint='ax')]

    result.extend(_set_properties(ax, axes_properties))

    result.append(Expression("{{ax}}.images = {{images}}",
                             ax=ax,
                             images=ax.images))
    result.append(Expression("{{ax}}.lines = {{lines}}",
                             ax=ax,
                             lines=ax.lines))
    return result

def mpl_subplot_fac(decomp, ax):
    return mpl_axes_fac(decomp, ax)

def mpl_figure_fac(decomp, fig):

    decomp.add_import('import matplotlib.pyplot as plt')
    result = [Expression("plt.figure()", output_ref=fig,
                         out_name_hint='fig')]
    result.extend(_set_properties(fig, figure_properties))

    for a in fig.axes:
        result.append(Expression("{{fig}}.add_axes( {{axes}} )",
                                 fig=fig, axes=a))
    return result

def mpl_rect_fac(decomp, rect):
    decomp.add_import('import matplotlib.pyplot as plt')
    result = [Expression("plt.Rectangle({{xy}}, {{width}}, {{height}})",
                         output_ref = rect,
                         xy = rect.get_xy(),
                         width = rect.get_width(),
                         height = rect.get_height(),
                         out_name_hint='rect')]
    result.extend(_set_properties(rect, rect_properties))
    return result
