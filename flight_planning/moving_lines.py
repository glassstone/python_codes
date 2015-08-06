import matplotlib 
matplotlib.rc_file('C:\\Users\\sleblan2\\Research\\python_codes\\file.rc')
import matplotlib.pyplot as plt
%matplotlib tk
import numpy as np
import scipy.io as sio
from mpl_toolkits.basemap import Basemap
import sys

class LineBuilder:
    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.connect()
        self.line.axes.format_coord = self.format_position_simple
        self.press = None
        self.contains = False

    def connect(self):
        'Function to connect all events'
        self.cid_onpress = self.line.figure.canvas.mpl_connect('button_press_event', self.onpress)
        self.cid_onrelease = self.line.figure.canvas.mpl_connect('button_release_event', self.onrelease)
        self.cid_onmotion = self.line.figure.canvas.mpl_connect('motion_notify_event',self.onmotion)
        self.cid_onkeypress = self.line.figure.canvas.mpl_connect('key_press_event',self.onkeypress)
        self.cid_onkeyrelease = self.line.figure.canvas.mpl_connect('key_release_event',self.onkeyrelease)

    def disconnect(self):
        'Function to disconnect all events (except keypress)'
        self.line.figure.canvas.mpl_disconnect(self.cid_onpress)
        self.line.figure.canvas.mpl_disconnect(self.cid_onrelease)
        self.line.figure.canvas.mpl_disconnect(self.cid_onmotion)
        self.line.figure.canvas.mpl_disconnect(self.cid_onkeyrelease)

    def onpress(self,event):
        'Function that enables either selecting a point, or creating a new point when clicked'
        #print 'click', event
        if event.inaxes!=self.line.axes: return
        tb = plt.get_current_fig_manager().toolbar
        if tb.mode!='': return
        self.contains, attrd = line.contains(event)
        if self.contains:
            print 'click is near point:',self.contains,attrd
            self.contains_index = attrd['ind']
            print 'index:', self.contains_index
            if not self.contains_index is 0:
                self.xy = self.xs[self.contains_index-1],self.ys[self.contains_index-1]
                self.line.axes.format_coord = self.format_position_distance
            else:
                self.line.axes.format_coord = self.format_position_simple
            self.line.axes.autoscale(enable=False)
            self.highlight_linepoint, = self.line.axes.plot(self.xs[self.contains_index],
                                                            self.ys[self.contains_index],'bo')
        else:
            self.xy = self.xs[-1],self.ys[-1]
            self.xs.append(event.xdata)
            self.ys.append(event.ydata)
            self.line.axes.format_coord = self.format_position_distance
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()
        self.press = event.xdata,event.ydata                                    
        sys.stdout.write('moving:')
        sys.stdout.flush()
        
    def onrelease(self,event):
        'Function to set the point location'
        print 'release'#,event
        self.press = None
        self.line.axes.format_coord = self.format_position_simple
        if self.contains:
            self.line.axes.lines.pop(1)
            self.contains = False
        self.line.figure.canvas.draw()

    def onmotion(self,event):
        'Function that moves the points to desired location'
        if event.inaxes!=self.line.axes: return
        if self.press is None: return
        sys.stdout.write("\r"+" moving: x=%2.5f, y=%2.5f" %(event.xdata,event.ydata))
        sys.stdout.flush()
        if self.contains:
            i = self.contains_index
            self.highlight_linepoint.set_data(event.xdata,event.ydata)
        else:
            i = -1
        self.xs[i] = event.xdata
        self.ys[i] = event.ydata
        self.line.set_data(self.xs,self.ys)
        self.line.figure.canvas.draw()

    def onkeypress(self,event):
        print 'pressed key',event.key,event.xdata,event.ydata
        if event.inaxes!=self.line.axes: return
        if (event.key=='s') | (event.key=='alt+s'):
            print 'Stopping interactive point selection'
            self.disconnect()
        if (event.key=='i') | (event.key=='alt+i'):
            print 'Starting interactive point selection'
            self.connect()
            self.line.axes.format_coord = self.format_position_simple
            self.press = None
            self.contains = False

    def onkeyrelease(self,event):
        #print 'released key',event.key
        if event.inaxes!=self.line.axes: return

    def format_position_simple(self,x,y):
        return 'x=%2.5f, y=%2.5f' % (x,y)

    def format_position_distance(self,x,y):
        x0,y0 = self.xy
        self.r = sqrt((x-x0)**2+(y-y0)**2)
        return 'x=%2.5f, y=%2.5f, d=%2.5f' % (x,y,self.r)
        
fig,ax = plt.subplots()
ax.set_title('line segments')
line, = ax.plot([0],[0],'ro-')
text = ('Press s to stop interaction\\n'
        'Press i to restart interaction\\n')
plt.text(1.0,0.1,text)
linebuilder = LineBuilder(line)
plt.show()
