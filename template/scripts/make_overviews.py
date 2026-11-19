"""Conceptual study diagrams; geometry and labels contain no empirical results."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from diagram_style import Diagram, RED, BLUE, INK, MUTED, RULE, PAPER, RED_PALE, BLUE_PALE

ROOT=Path(__file__).resolve().parents[2]


def destination(paper,output):
    if output:return Path(output)/(paper+'-fig1-overview.pdf')
    directory='p1-scoring-the-future'if paper=='p1'else'p2-hackability-measured'
    return ROOT/directory/'paper/figures/fig1-overview.pdf'


def p1(output=None):
    d=Diagram(300)
    d.heading('A','Assigned document inclusion',3,'Random complementary corpora; compare both copies on the same questions')
    # Illustrate one question in half A. The complete question/answer document,
    # rather than an isolated answer token, is the assigned intervention.
    d.document(20,45,24,31,RED,RED_PALE)
    d.text(51,44,'Question + answer','title',bold=True)
    d.text(51,58,'Assigned to half A','note',colour=MUTED)
    d.text(20,88,'Other documents','note',colour=MUTED)
    d.text(20,100,'form half B','note',colour=MUTED)
    d.arrow(149,59,181,59,RED)
    d.arrow(149,101,181,101,BLUE)
    d.rect(188,43,106,32,RED_PALE,edge='none')
    d.rect(188,85,106,32,BLUE_PALE,edge='none')
    d.rule(188,43,106,RED,1.5);d.rule(188,85,106,BLUE,1.5)
    d.text(197,48,'Copy A','title',colour=RED,bold=True)
    d.text(197,61,'Trained on half A','note')
    d.text(197,90,'Copy B','title',colour=BLUE,bold=True)
    d.text(197,103,'Trained on half B','note')
    d.arrow(301,59,328,59,RED);d.arrow(301,101,328,101,BLUE)
    d.text(340,40,'Same question','title',bold=True)
    d.text(340,56,'Brier loss: included','body',colour=RED)
    d.text(340,98,'Brier loss: excluded','body',colour=BLUE)
    d.line(450,62,457,62,MUTED,.7)
    d.line(457,62,457,104,MUTED,.7)
    d.line(450,104,457,104,MUTED,.7)
    d.text(340,116,'Paired: excluded − included','note',colour=MUTED)
    d.text(20,128,'Membership reverses for questions in half B. Corpus content changes with assignment.','note',colour=MUTED)
    d.text(20,141,'Decoding sensitivity: ordinary versus constrained output, specified post-hoc.','note',colour=MUTED)
    d.rule(0,159,d.width)

    d.heading('B','Historical cutoff comparison',171)
    d.text(18,187,'Match category, horizon and initial crowd probability','note',colour=MUTED)
    d.text(20,208,'Earlier cohort','body',colour=BLUE)
    d.text(20,229,'Later cohort','body',colour=RED)
    # Timeline positions are illustrative and intentionally carry no dates.
    cutoff=237
    d.line(cutoff,204,cutoff,240,MUTED,.6,linestyle=(0,(2,2)))
    d.text(cutoff,195,'Cutoff','small',ha='center',colour=MUTED)
    for y,left,right,col in [(214,124,205,BLUE),(235,264,345,RED)]:
        d.line(left,y,right,y,col,1.8);d.dot(left,y,col,open=True);d.dot(right,y,col)
    d.dot(126,248,MUTED,open=True);d.text(134,244,'Created','small',colour=MUTED)
    d.dot(199,248,MUTED);d.text(207,244,'Resolved','small',colour=MUTED)
    d.arrow(277,248,345,248,MUTED,.6);d.text(352,244,'Time','small',colour=MUTED)
    d.text(374,211,'Same closed-book','body',bold=True)
    d.text(374,224,'forecast protocol','body',bold=True)
    d.arrow(349,224,365,224,MUTED)
    d.rule(0,261,d.width)

    d.heading('C','Prospective commitment',273)
    # The short bottom sequence carries no live results and no implied dates.
    d.text(165,274,'Rules','body',bold=True)
    d.arrow(197,279,212,279,MUTED)
    d.text(221,274,'Forecast + SHA-256','body',colour=RED,bold=True)
    d.arrow(314,279,329,279,MUTED)
    d.text(338,274,'Resolve later','body',bold=True)
    d.text(338,287,'No live scores yet','small',colour=MUTED)
    path=destination('p1',output);d.finish(path);return path


def p2(output=None):
    d=Diagram(252)
    for x,letter,title in [(0,'A','Program sources'),(166,'B','Paired assessment'),(337,'C','Task-level comparison')]:
        d.text(x+2,3,letter,'panel',colour=RED,bold=True);d.text(x+18,3,title,'panel',bold=True)
    d.text(2,21,'Separate training and evaluation tasks; fixed task specifications and resource limits','note',colour=MUTED)
    d.rule(0,36,d.width)
    # Sources: these are two different populations, not two attack arms.
    d.rule(4,54,138,INK,1.5)
    d.text(4,62,'Ordinary sampling','title',bold=True)
    d.text(4,77,'Frozen coding models','body')
    d.text(4,89,'Fixed budget; no directed search','note',colour=MUTED)
    d.rule(4,124,138,RED,1.5)
    d.text(4,132,'Separate training policy','title',colour=RED,bold=True)
    d.text(4,147,'Grader reward on training tasks','note')
    d.text(4,160,'Saved baseline and checkpoints','note',colour=MUTED)
    d.arrow(146,83,160,83,MUTED)
    d.arrow(146,149,160,149,MUTED)
    # A small crossed design makes the independent axes visible without a
    # nested flowchart. It is a design matrix, not a heatmap of outcomes.
    d.text(169,48,'Grader configurations','title',colour=RED,bold=True)
    d.text(244,64,'Same process','small',ha='center',colour=MUTED)
    d.text(298,64,'Host-held','small',ha='center',colour=MUTED)
    for y,label in [(79,'Visible'),(98,'Extended'),(117,'Hardened')]:
        d.text(169,y+3,label,'note')
        for x in (227,281):
            d.rect(x,y,36,15,RED_PALE,edge='none');d.rule(x,y,36,RED,.7)
            code=label[0]+'–'+('S'if x==227 else'H')
            d.text(x+18,y+3,code,'small',ha='center',colour=RED)
    d.text(169,147,'Held-out oracle','title',colour=BLUE,bold=True)
    d.text(169,161,'Hidden tests and references','note')
    d.text(169,181,'Each program receives both verdicts','small',colour=MUTED)
    d.arrow(321,111,333,111,MUTED)
    # The joint event is defined operationally, without asserting correctness.
    d.text(341,48,'Accepted-but-wrong event','title',bold=True)
    d.text(341,65,'Grader accepts; oracle rejects','note')
    d.rect(341,83,126,29,RED_PALE,edge='none')
    d.text(348,89,r'$q = \Pr(G=1,\ O=0)$','title',colour=RED)
    d.text(341,126,r'Discovery $D(B)$','title',bold=True)
    d.text(341,140,'Event found within budget B','note')
    d.text(341,158,r'Training change $\Delta q$','title',bold=True)
    d.text(341,172,'Checkpoint minus baseline','note')
    d.rule(341,191,126,BLUE,.8)
    d.text(341,197,'Associate across tasks','title',colour=BLUE,bold=True)
    d.rule(0,218,d.width)
    d.text(3,229,'Grader card','title',bold=True)
    d.text(82,229,'Discovery · conditional rejection · test adequacy · revisit date','body')
    d.text(3,243,'Programs execute in isolation. Seeded hints are outside this study.','small',colour=MUTED)
    path=destination('p2',output);d.finish(path);return path


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--paper',choices=('p1','p2','both'),default='both');parser.add_argument('--output-dir',type=Path);args=parser.parse_args()
    paths=[]
    if args.paper in('p1','both'):paths.append(p1(args.output_dir))
    if args.paper in('p2','both'):paths.append(p2(args.output_dir))
    if args.output_dir:
        inputs=[Path(__file__),Path(__file__).resolve().parents[1]/'diagram_style.py',Path(__file__).resolve().parents[1]/'figure_style.py']
        report={'schema':'hpr-conceptual-diagrams-v2','empirical_data_used':False,'source_sha256':{str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest()for p in inputs},'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},'minimum_font_pt':7,'width_pt':470.551968}
        (args.output_dir/'provenance.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
