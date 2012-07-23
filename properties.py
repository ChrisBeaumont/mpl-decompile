plot_properties = (
    ('aa', True),
    ('alpha', None),
    ('color', None),
    ('dash_capstyle', 'butt'),
    ('dash_joinstyle', 'round'),
    ('fillstyle', 'full'),
    ('label', None),
    ('linestyle', '-'),
    ('linewidth', 1.0),
    ('marker', 'None'),
    ('markeredgecolor', None),
    ('markeredgewidth', 0.5),
    ('markerfacecolor', None),
    ('markerfacecoloralt', 'none'),
    ('solid_capstyle', 'projecting'),
    ('solid_joinstyle', 'round'),
    ('url', None),
    ('visible', True),
    ('zorder', None)
    )

#XXX TODO: cmap
#XXX some of these are numpy arrays. need to recursively decompile
scatter_properties = (
    ('alpha', None),
    ('dashes', [(None, None)]),
    ('edgecolor', [[0., 0., 0., 1.]]),
    ('facecolor', [[0., 0., 0., 1.]]),
    ('label', None),
    ('linestyle', [(None, None)]),
    ('linewidth', (1.0,)),
#('sizes', [20]), np masked array
    ('urls', None),
    ('visible', True),
    ('zorder', None)
    )
