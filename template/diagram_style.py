"""Measured, final-size primitives for conceptual figures, without empirical data."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon
from figure_style import apply, save, TEXT_IN, RED, BLUE, INK

MUTED='#60666B'
RULE='#CCD0D2'
PAPER='#F6F6F4'
RED_PALE='#F7EBEB'
BLUE_PALE='#EAF2F7'
WIDTH=TEXT_IN*72
TYPE={'panel':9,'title':8.5,'body':8,'note':7.3,'small':7}

class Diagram:
    def __init__(self,height):
        apply()
        import matplotlib as mpl
        mpl.rcParams['mathtext.cal']='XCharter'
        mpl.rcParams['svg.hashsalt']='hyperprior-conceptual-v2'
        self.fig=plt.figure(figsize=(TEXT_IN,height/72))
        self.ax=self.fig.add_axes([0,0,1,1])
        self.ax.set(xlim=(0,WIDTH),ylim=(height,0));self.ax.axis('off')
        self.width=WIDTH;self.height=height;self.texts=[]
    def text(self,x,y,value,style='body',colour=INK,bold=False,ha='left',va='top',**kwargs):
        artist=self.ax.text(x,y,value,fontsize=TYPE[style],color=colour,fontweight='bold'if bold else'normal',ha=ha,va=va,linespacing=1.25,**kwargs)
        self.texts.append(artist);return artist
    def rect(self,x,y,w,h,face='white',edge=RULE,lw=.6):
        self.ax.add_patch(Rectangle((x,y),w,h,facecolor=face,edgecolor=edge,linewidth=lw))
    def rule(self,x,y,w,colour=RULE,lw=.55):self.ax.plot([x,x+w],[y,y],color=colour,lw=lw,solid_capstyle='butt')
    def line(self,x1,y1,x2,y2,colour=RULE,lw=.7,**kwargs):self.ax.plot([x1,x2],[y1,y2],color=colour,lw=lw,**kwargs)
    def arrow(self,x1,y1,x2,y2,colour=INK,lw=.8,connectionstyle='arc3'):
        self.ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=7,lw=lw,color=colour,shrinkA=0,shrinkB=0,connectionstyle=connectionstyle))
    def heading(self,letter,title,y,subtitle=None):
        self.text(2,y,letter,'panel',colour=RED,bold=True)
        self.text(18,y,title,'panel',bold=True)
        if subtitle:self.text(18,y+14,subtitle,'note',colour=MUTED)
    def dot(self,x,y,colour=INK,radius=2.2,open=False):
        from matplotlib.patches import Circle
        self.ax.add_patch(Circle((x,y),radius,facecolor='white'if open else colour,edgecolor=colour,lw=.8))
    def document(self,x,y,w=21,h=27,colour=INK,fill='white'):
        self.ax.add_patch(Polygon([(x,y),(x+w-5,y),(x+w,y+5),(x+w,y+h),(x,y+h)],closed=True,facecolor=fill,edgecolor=colour,lw=.65))
        self.line(x+w-5,y,x+w-5,y+5,colour,.55);self.line(x+w-5,y+5,x+w,y+5,colour,.55)
        for dy,end in [(11,w-4),(16,w-4),(21,w-8)]:self.line(x+4,y+dy,x+end,y+dy,colour,.5)
    def finish(self,path):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        self.fig.canvas.draw()
        renderer=self.fig.canvas.get_renderer();canvas=self.fig.bbox
        outside=[]
        for text in self.texts:
            box=text.get_window_extent(renderer)
            if box.x0<canvas.x0-.5 or box.x1>canvas.x1+.5 or box.y0<canvas.y0-.5 or box.y1>canvas.y1+.5:outside.append(text.get_text())
        if outside:raise ValueError('Diagram text leaves the final canvas: '+repr(outside))
        save(self.fig,path)
        self.fig.savefig(path.with_suffix('.svg'),format='svg',metadata={'Creator':'HyperPrior Research','Date':None})
        plt.close(self.fig)
