import astropy.io.fits as pyfits

from bokeh.io import output_file, show
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, Range1d, HoverTool
from bokeh.plotting import figure, output_file
from bokeh.util.hex import hexbin

import ugali.utils.projector

#####

infile = 'dr1_m2_dered_test.fits'
reader = pyfits.open(infile)
data = reader[1].data
reader.close()

#data = data[0:1000]
data = data[data['MAG_AUTO_G_DERED'] < 26.]

print len(data)

ra_target, dec_target = 323.36, -0.82

proj = ugali.utils.projector.Projector(ra_target, dec_target)
x, y = proj.sphereToImage(data['RA'], data['DEC'])

mag = data['MAG_AUTO_G_DERED']
color = data['MAG_AUTO_G_DERED'] - data['MAG_AUTO_R_DERED']

# create a column data source for the plots to share
source = ColumnDataSource(data=dict(x0=x, 
                                    y0=y, 
                                    x1=color, 
                                    y1=mag,
                                    ra=data['RA'],
                                    dec=data['DEC'],
                                    coadd_object_id=data['COADD_OBJECT_ID']))

# There is a little bit of trickery here to a create custom hover tool on both panels
hover_left = HoverTool(tooltips=[("(RA,DEC)", "(@ra, @dec)"),
                                 ("(g-r,g)", "(@x1, @y1)"),
                                 ("coadd_object_id", "@coadd_object_id")])
hover_right = HoverTool(tooltips=[("(RA,DEC)", "(@ra, @dec)"),
                                  ("(g-r,g)", "(@x1, @y1)"),
                                  ("coadd_object_id", "@coadd_object_id")])
TOOLS = "box_zoom,box_select,lasso_select,reset,help"
TOOLS_LEFT = [hover_left, TOOLS]
TOOLS_RIGHT = [hover_right, TOOLS]

#TOOLS_LEFT = ["box_zoom,box_select,lasso_select,hover,reset,help"]
#TOOLS_RIGHT = ["box_zoom,box_select,lasso_select,hover,reset,help"]

# create a new plot and add a renderer
left = figure(tools=TOOLS_LEFT, plot_width=500, plot_height=500, output_backend="webgl",
              title='Spatial: Centered on (RA, Dec) = (%.2f, %.2f)'%(ra_target, dec_target))
left.circle('x0', 'y0', hover_color='firebrick', source=source,
            selection_fill_color='steelblue', selection_line_color='steelblue',
            nonselection_fill_color='silver', nonselection_line_color='silver')
left.x_range = Range1d(0.3, -0.3)
left.y_range = Range1d(-0.3, 0.3)
left.xaxis.axis_label = 'Delta RA'
left.yaxis.axis_label = 'Delta DEC'

# create another new plot and add a renderer
right = figure(tools=TOOLS_RIGHT, plot_width=500, plot_height=500, output_backend="webgl",
               title='CMD')
right.circle('x1', 'y1', hover_color='firebrick', source=source, 
             selection_fill_color='steelblue', selection_line_color='steelblue',
             nonselection_fill_color='silver', nonselection_line_color='silver')
right.x_range = Range1d(-0.5, 2.5)
right.y_range = Range1d(26., 16.)
right.xaxis.axis_label = 'g - r'
right.yaxis.axis_label = 'g'

p = gridplot([[left, right]])

output_file("bokeh_m2_example.html", title="M2 Example")

show(p)

