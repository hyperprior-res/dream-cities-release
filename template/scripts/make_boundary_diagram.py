"""Conceptual process boundaries and oracle-relative events; no executable content."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from diagram_style import Diagram, RED, BLUE, INK, MUTED, RULE, RED_PALE
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parents[2]


def boundary(d,x,width):
    d.ax.add_patch(Rectangle((x,67),width,48,facecolor='none',edgecolor=MUTED,linewidth=.7,linestyle=(0,(4,2))))
    d.rect(x+9,62,74,11,'white',edge='none')
    d.text(x+12,62,'Isolated process','small',colour=MUTED)


def draw(output=None):
    d=Diagram(280)
    d.heading('A','Same-process comparison',3)
    d.text(249,3,'B','panel',colour=RED,bold=True);d.text(266,3,'Host-held comparison','panel',bold=True)
    d.text(18,20,'Expected values enter the candidate process','note',colour=MUTED)
    d.text(266,20,'Expected values stay outside that process','note',colour=MUTED)
    boundary(d,4,218);boundary(d,250,218)
    # Actual direction of information in the unchanged implementation.
    d.text(21,43,'Inputs + expected values','body')
    d.arrow(56,56,56,77,MUTED)
    d.text(20,81,'Candidate','title',colour=RED,bold=True)
    d.text(20,94,'program','title',colour=RED,bold=True)
    d.arrow(89,91,115,91,MUTED)
    d.text(123,80,'Compare with','body',bold=True)
    d.text(123,93,'expected values','body',bold=True)
    d.arrow(165,106,165,134,RED)
    d.rect(126,117,80,12,'white',edge='none')
    d.text(129,119,'Reported summary','small',colour=RED)
    d.text(114,140,'Host validates','title',bold=True)
    d.text(89,154,'Status, schema and test count','small')
    d.text(212,140,r'$G$','title',colour=RED,bold=True)
    d.arrow(197,145,207,145,RED)
    d.text(266,43,'Inputs only','body')
    d.arrow(298,56,298,81,MUTED)
    d.text(266,81,'Candidate','title',colour=RED,bold=True)
    d.text(266,94,'program','title',colour=RED,bold=True)
    d.arrow(335,91,359,91,MUTED)
    d.text(369,80,'Serialised','body')
    d.text(369,93,'outputs','body')
    d.arrow(404,106,404,134,BLUE)
    d.rect(377,117,54,12,'white',edge='none')
    d.text(381,119,'JSON values','small',colour=BLUE)
    d.text(266,139,'Expected','note',colour=BLUE)
    d.text(266,151,'values','note',colour=BLUE)
    d.arrow(315,146,337,146,BLUE)
    d.text(344,140,'Host compares','title',colour=BLUE,bold=True)
    d.text(344,154,'Validated outputs against expectations','small')
    d.text(456,140,r'$G$','title',colour=BLUE,bold=True)
    d.arrow(438,145,450,145,BLUE)
    d.text(4,175,'Both variants require successful execution and a valid output format; exit status alone never establishes a pass.','small',colour=MUTED)
    d.rule(0,192,d.width)
    d.heading('C','Oracle-relative event definitions',203)
    d.text(266,204,'q: all draws · f: oracle-passing draws','small',colour=MUTED)
    d.text(177,223,'Grader rejects  G = 0','title',bold=True,ha='center')
    d.text(371,223,'Grader accepts  G = 1','title',bold=True,ha='center')
    d.rule(0,237,d.width)
    d.text(4,242,'Oracle rejects  O = 0','note')
    d.text(177,242,'Agreement','body',colour=MUTED,ha='center')
    d.text(371,241,r'$q = \Pr(G=1,\ O=0)$','title',colour=RED,ha='center')
    d.text(4,260,'Oracle accepts  O = 1','note')
    d.text(177,259,r'$f = \Pr(G=0\mid O=1)$','title',colour=BLUE,ha='center')
    d.text(371,260,'Agreement','body',colour=MUTED,ha='center')
    out=Path(output)if output else ROOT/'p2-hackability-measured/paper/figures/trust-boundary.pdf'
    d.finish(out);return out


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args();draw(args.output)
if __name__=='__main__':main()
