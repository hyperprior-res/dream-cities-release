"""A final-size measurement sheet; absent observations remain unavailable."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from diagram_style import Diagram, RED, BLUE, INK, MUTED, RULE, PAPER
import matplotlib as mpl
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MaxNLocator, PercentFormatter
import numpy as np

HEIGHT=601.2


def finite_rate(value):
    if type(value)not in(int,float)or not math.isfinite(value)or not 0<=value<=1:
        raise ValueError('A recorded rate must be finite and lie in the unit interval')
    return value


def metric(value):
    if value is None:return 'Unavailable'
    if type(value)in(int,float):estimate=value;interval=None
    elif isinstance(value,dict)and value.get('estimate')is not None:
        estimate=value['estimate'];interval=(value.get('lower'),value.get('upper'))
    else:return 'Unavailable'
    answer=f'{finite_rate(estimate):.1%}'
    if interval and all(x is not None for x in interval):
        lo,hi=map(finite_rate,interval)
        if lo>hi:raise ValueError('Invalid recorded rate interval')
        answer+=f'  [{lo:.1%}, {hi:.1%}]'
    return answer


def count(value):
    if value is None:return 'Unavailable'
    if type(value)not in(int,float)or not math.isfinite(value)or value<0 or int(value)!=value:
        raise ValueError('A recorded count must be a finite nonnegative integer value')
    return f'{int(value):,}'


def wrap_points(text,width,size=8):
    """Wrap using the printed font metrics, without dropping words."""
    font=FontProperties(family='XCharter',size=size)
    dpi=mpl.rcParams['figure.dpi']
    renderer=RendererAgg(1,1,dpi)
    def length(line):
        # Advance widths include spaces and match the canvas-bound check. Ink
        # outlines underestimate long prose lines at the rendered font size.
        return renderer.get_text_width_height_descent(line,font,ismath=False)[0]*72/dpi if line.strip()else 0
    lines=[]
    for paragraph in str(text).split('\n'):
        line=''
        for word in paragraph.split():
            proposal=(line+' '+word).strip()
            if length(proposal)<=width:line=proposal
            elif line:lines.append(line);line=word
            else:raise ValueError('An unbreakable card label exceeds the final width')
            if length(line)>width:raise ValueError('An unbreakable card label exceeds the final width')
        lines.append(line)
    return lines


def paragraph(d,x,y,text,width,size=8,colour=INK,leading=10.4):
    lines=wrap_points(text,width,size)
    for index,line in enumerate(lines):
        artist=d.text(x,y+index*leading,line,'body',colour=colour)
        artist.set_fontsize(size)
    return y+len(lines)*leading


def field(d,x,y,label,text,width):
    d.text(x,y,label,'title',bold=True)
    return paragraph(d,x,y+13,text,width,size=7.8)


def section(d,y,label,right=None):
    d.rule(10,y,450)
    d.text(10,y+9,label,'title',colour=RED,bold=True)
    if right:d.text(460,y+9,right,'small',colour=MUTED,ha='right')
    return y+20


def rate_parts(value):
    if value is None:return 'Unavailable','Unavailable'
    if isinstance(value,dict)and value.get('estimate')is None:
        lower,upper=value.get('missing_data_lower'),value.get('missing_data_upper')
        if lower is not None and upper is not None:
            lower,upper=finite_rate(lower),finite_rate(upper)
            if lower>upper:raise ValueError('Invalid missing-data bounds')
            return 'Unavailable',f'Bounds [{lower:.1%}, {upper:.1%}]'
        return 'Unavailable','Unavailable'
    def precision(values):
        # Retain a visible nonzero digit for small recorded rates. A rounded
        # displayed zero must not hide an observed conditional rejection.
        nonzero=[finite_rate(v) for v in values if v is not None and v>0]
        return next((digits for digits in range(1,9)
                     if all(round(v*100,digits)>0 for v in nonzero)),8)
    if type(value)in(int,float):
        digits=precision([value]);return f'{finite_rate(value):.{digits}%}','Unavailable'
    metric(value)
    digits=precision([value['estimate'],value.get('lower'),value.get('upper')])
    interval='Unavailable'
    if value.get('lower')is not None and value.get('upper')is not None:
        interval=f"[{value['lower']:.{digits}%}, {value['upper']:.{digits}%}]"
    return f"{value['estimate']:.{digits}%}",interval


def historical_reference(measurements):
    """Prefer the explicit historical field, even when its value is unavailable."""
    key='historical_canonical_reference_rejection_rate'
    if key not in measurements:key='canonical_reference_false_rejection_rate'
    return key,measurements.get(key)


def condition_lines(conditions):
    """Describe supplied current conditions without borrowing historical limits."""
    if conditions is None:return ['Current measurement conditions: unavailable.']
    if not isinstance(conditions,dict):raise ValueError('Measurement conditions must be an object or null')
    def number(key,unit):
        value=conditions.get(key)
        if value is None:return 'unavailable'
        if type(value)not in(int,float)or not math.isfinite(value)or value<0:
            raise ValueError('Invalid recorded measurement condition: '+key)
        return f'{value} {unit}'
    def label(value):
        if value is None:return 'unavailable'
        if not isinstance(value,str)or not value.strip():raise ValueError('Empty or invalid condition label')
        return value
    host=conditions.get('host')
    if host is None:host={}
    if not isinstance(host,dict):raise ValueError('Condition host must be an object')
    workers=conditions.get('lane_workers')
    if workers is None:worker_label='unavailable'
    elif not isinstance(workers,list)or not workers or any(type(x)is not int or x<=0 for x in workers):
        raise ValueError('Lane workers must be positive integer counts')
    else:worker_label=' + '.join(map(str,workers))
    return [
        'Current measurement: '+label(conditions.get('execution_location'))+'; '+label(host.get('cpu_model'))+'; kernel '+label(host.get('kernel'))+'.',
        'Wall: '+number('wall_seconds','s')+'; CPU soft / hard: '+number('cpu_seconds','s')+' / '+number('hard_cpu_seconds','s')+'; lane workers: '+worker_label+'.',
        'Memory: '+number('memory_mb','MiB')+'; scratch: '+number('scratch_mb','MiB')+'; output: '+number('output_bytes','bytes')+'.',
    ]


def curve_panel(d,top,curve,interval_description=None,compact=False):
    points=[] if not curve else sorted(curve,key=lambda row:row['budget'])
    budgets=[row['budget']for row in points]
    if any(type(b)is not int or b<=0 for b in budgets)or len(set(budgets))!=len(budgets):
        raise ValueError('Discovery budgets must be unique positive integers')
    values=[];intervals=[];bounds=[];valid=[];missing=[]
    for row in points:
        b=row['budget'];estimate=row.get('estimate')
        if estimate is None:missing.append(b)
        else:valid.append((b,finite_rate(estimate)));values.append(estimate)
        lo,hi=row.get('lower'),row.get('upper')
        if (lo is None)!=(hi is None):raise ValueError('Incomplete recorded discovery interval')
        if lo is not None:
            lo,hi=finite_rate(lo),finite_rate(hi)
            if lo>hi:raise ValueError('Invalid recorded discovery interval')
            if estimate is not None:intervals.append((b,lo,hi));values.extend((lo,hi))
        low,high=row.get('missing_data_lower'),row.get('missing_data_upper')
        if (low is None)!=(high is None):raise ValueError('Incomplete missing-data bounds')
        if low is not None:
            low,high=finite_rate(low),finite_rate(high)
            if low>high:raise ValueError('Invalid missing-data bounds')
            if estimate is None:bounds.append((b,low,high));values.extend((low,high))
    method=interval_description or'Interval method unavailable in the supplied card.'
    if len(wrap_points(method,365,7))>1:raise ValueError('Use a concise interval description that fits the card heading')
    d.text(10,top-14,method,'small',colour=MUTED)
    plot_height=82 if compact else 102
    ax=d.fig.add_axes([50/d.width,1-(top+plot_height)/d.height,404/d.width,plot_height/d.height])
    if values:
        limit=min(1,max(values)*1.15)
        if limit==0:limit=.01
        upper=min(1,float(MaxNLocator(nbins=4,steps=[1,2,2.5,5,10]).tick_values(0,limit)[-1]))
        y=[np.nan if row.get('estimate')is None else row['estimate']for row in points]
        ax.plot(budgets,y,color=RED,lw=1.3,marker='o',ms=3.6,zorder=3)
        # Draw interval segments directly: percentile intervals need not contain
        # their point estimate, so symmetric error-bar distances are invalid.
        for b,lo,hi in intervals:
            ax.vlines(b,lo,hi,color=RED,lw=1.1,alpha=.85,zorder=2)
            ax.plot([b,b],[lo,hi],linestyle='none',marker='_',ms=5,color=RED)
        for b,lo,hi in bounds:
            ax.vlines(b,lo,hi,color=MUTED,lw=1.1,linestyle=(0,(3,2)),zorder=2)
            ax.plot([b,b],[lo,hi],linestyle='none',marker='_',ms=6,color=MUTED)
        ax.set_ylim(0,upper)
        locator=MaxNLocator(nbins=4,min_n_ticks=3)
        ax.yaxis.set_major_locator(locator)
        ticks=locator.tick_values(0,upper)
        decimals=next((places for places in range(7)if all(math.isclose(t*100,round(t*100,places),abs_tol=1e-9)for t in ticks)),6)
        ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=decimals))
        ax.set_xticks(budgets)
        if len(budgets)>1:ax.set_xlim(min(budgets)-.035*(max(budgets)-min(budgets)),max(budgets)+.035*(max(budgets)-min(budgets)))
        else:ax.set_xlim(budgets[0]-.5,budgets[0]+.5)
        ax.set_ylabel('Discovery probability',fontsize=8)
        ax.set_xlabel('Discovery budget, B',fontsize=8,labelpad=5)
        ax.tick_params(labelsize=7.3)
        ax.grid(axis='y',color='#E4E5E5',lw=.5)
        ax.spines[['top','right']].set_visible(False)
        scale=f'Axis: 0–{100*upper:.{decimals}f}%'
        d.text(460,top-14,scale,'small',colour=MUTED,ha='right')
    else:
        ax.axis('off')
        ax.text(.5,.61,'Discovery curve unavailable',transform=ax.transAxes,fontsize=9,color=MUTED,ha='center')
        ax.text(.5,.40,'No numeric estimate is inferred.',transform=ax.transAxes,fontsize=8,color=MUTED,ha='center')
        upper=None
    note='Points: recorded estimates. Bars: recorded intervals.'if values else'No discovery estimates are supplied.'
    if bounds:note+=' Dashed: missing-data bounds.'
    if missing:note+=' Unavailable B: '+', '.join(map(str,missing))+'.'
    note_end=paragraph(d,10,top+plot_height+27,note,450,size=7,colour=MUTED,leading=9)
    return note_end+4,{'axis_upper':upper,'missing_budgets':missing,'point_count':len(valid),'interval_count':len(intervals),'bound_count':len(bounds)}


def render(source,destination):
    source,destination=Path(source),Path(destination)
    raw=source.read_bytes();card=json.loads(raw)
    for key in('configuration','task_specification','oracle','sampler_class','scope','test_strength','exposure','metrics','shelf_life','revisit_date'):
        if key not in card:raise ValueError('Missing card field: '+key)
    measurements=card['metrics'];d=Diagram(HEIGHT)
    conditions=measurements.get('measurement_conditions')
    compact=conditions is not None
    shift=4 if compact else 0
    d.text(10,7,'GRADER CARD','title',colour=RED,bold=True)
    d.text(460,7,card.get('instrument','hpr-audit')+' / '+card.get('version',''),'small',colour=MUTED,ha='right')
    title=d.text(10,23,card['configuration'].replace('_',' · '),'panel',bold=True);title.set_fontsize(15)
    d.text(10,45,'Test strength: '+card['test_strength']+'    Comparison: '+card['exposure'],'body',colour=MUTED)
    d.rule(10,60-shift,450,INK,.9)
    left=field(d,10,70-shift,'Task specification',measurements.get('task_description',card['task_specification']),213)
    right=field(d,249,70-shift,'Oracle',card['oracle'],211)
    y=max(left,right)+(6 if compact else 10)
    d.text(10,y,'Sampler and budget','title',bold=True)
    y=paragraph(d,10,y+(12 if compact else 14),card['sampler_class'],450,size=7.8)
    y=paragraph(d,10,y+(1 if compact else 3),measurements.get('budget_description','Sampling budget unavailable in the supplied card.'),450,size=7.5,colour=MUTED,leading=10)
    condition_text=condition_lines(conditions)
    if compact:
        for line in condition_text:y=paragraph(d,10,y+1,line,450,size=7,colour=MUTED,leading=8.5)
    top=section(d,y+(3 if compact else 11),'Accepted-but-wrong discovery under ordinary sampling')
    bottom,chart_metadata=curve_panel(d,top+(13 if compact else 15),measurements.get('budget_curve'),measurements.get('interval_description'),compact)
    # Coverage quantities are recorded totals; none is reconstructed from a rate.
    counts=card.get('execution_counts',{})
    coverage=[('Recorded samples',measurements.get('samples',counts.get('samples'))),
              ('Accepted-but-wrong',measurements.get('accepted_wrong_count',counts.get('accepted_but_oracle_failed'))),
              ('Joint verdicts missing',measurements.get('joint_missing_count'))]
    for x,(label,value)in zip((10,167,324),coverage):
        d.text(x,bottom,label,'small',colour=MUTED)
        d.text(x,bottom+11,count(value),'title',bold=True)
    y=section(d,bottom+(22 if compact else 25),'Rejection measures')
    for x,text,ha in [(10,'Population','left'),(265,'Rate','right'),(368,'Interval / bounds','right'),(460,'Denominator','right')]:d.text(x,y,text,'small',colour=MUTED,ha=ha)
    reference_key,reference_value=historical_reference(measurements)
    for offset,label,value in [(13,'Given oracle acceptance',measurements.get('false_rejection_rate')),(27,'Original canonical references',reference_value)]:
        estimate,interval=rate_parts(value);den=value.get('denominator')if isinstance(value,dict)else None
        d.text(10,y+offset,label,'body');d.text(265,y+offset,estimate,'body',colour=BLUE,ha='right');d.text(368,y+offset,interval,'body',ha='right');d.text(460,y+offset,count(den),'body',ha='right')
    rejection_method=measurements.get('rejection_interval_description','Rejection interval method unavailable in the supplied card.')
    rejection_end=paragraph(d,10,y+39,rejection_method,450,size=7,colour=MUTED,leading=9)
    historical_scope=measurements.get('historical_reference_scope')
    if historical_scope is not None:
        rejection_end=paragraph(d,10,rejection_end+1,historical_scope,450,size=7,colour=MUTED,leading=8.5)
    classes=measurements.get('failure_classes')
    static_n=classes.get('accepted_wrong_count')if isinstance(classes,dict)else None
    y=section(d,rejection_end+3,'Static syntax evidence','Accepted-but-wrong n: '+count(static_n))
    if classes and 'ast_label_counts'in classes and 'token_label_counts'in classes:
        names=[('environment_access','Environment'),('visible_example_branch','Example branch'),('mixed_evidence','Mixed'),('no_flagged_evidence','Unflagged'),('insufficient_evidence','Unanalysable')]
        positions=(110,198,286,374,460)
        for x,(_,label)in zip(positions,names):d.text(x,y,label,'small',ha='right',colour=MUTED)
        for offset,fieldname,label in [(14,'ast_label_counts','AST'),(27,'token_label_counts','Tokens')]:
            observed=classes[fieldname]
            if set(observed)-{key for key,_ in names}:raise ValueError('Unknown static-evidence category would be omitted')
            for value in observed.values():count(value)
            if static_n is not None and sum(observed.values())!=static_n:raise ValueError('Static category counts do not exhaust their recorded denominator')
            d.text(10,y+offset,label,'body')
            for x,(key,_)in zip(positions,names):
                value=observed.get(key,0 if static_n is not None else None)
                d.text(x,y+offset,count(value),'body',ha='right')
        y=paragraph(d,10,y+39,'Automated labels among accepted-but-wrong samples; no human validation or mechanism proof.',450,size=7,colour=MUTED,leading=9)
    elif classes:
        lines=[]
        for key,value in classes.items():
            label=key.replace('_',' ')
            if isinstance(value,dict)and value.get('count')is not None:
                text=count(value['count'])+'/'+count(value.get('denominator'))
            else:text=metric(value)if isinstance(value,dict)else str(value)
            lines.append(label+': '+text)
        y=paragraph(d,10,y,'; '.join(lines),450,size=7.3,colour=MUTED,leading=9.4)
    else:y=paragraph(d,10,y,'Static-evidence counts unavailable. Ordinary sampling does not establish adaptive tampering resistance.',450,size=7.3,colour=MUTED,leading=9.4)
    y=section(d,y+(4 if compact else 7),'Validity and revisit')
    y=paragraph(d,10,y,card['scope'],450,size=7.3,leading=9.4)
    life=card['shelf_life'];life_note=('Unavailable. '+life.get('reason','No reason recorded.'))if life.get('estimate')is None else str(life['estimate'])
    y=paragraph(d,10,y+4,'Shelf life: '+life_note,450,size=7.3,colour=MUTED,leading=9.4)
    if y>HEIGHT-27:raise ValueError(f'Card content reaches {y:.1f} pt, beyond the one-page measurement sheet; shorten supplied descriptions without dropping evidence')
    d.rule(10,HEIGHT-21,450)
    d.text(10,HEIGHT-12,'Administrative revisit: '+card['revisit_date'],'small',colour=MUTED)
    d.text(460,HEIGHT-12,'Card SHA-256: '+hashlib.sha256(raw).hexdigest()[:16],'small',colour=MUTED,ha='right')
    d.finish(destination)
    destination.with_suffix('.provenance.json').write_text(json.dumps({'source_file':str(source),'source_sha256':hashlib.sha256(raw).hexdigest(),'configuration':card['configuration'],'metrics':measurements,'card':card,'unavailable_is_not_zero':True,'chart_display':chart_metadata,'historical_reference_field':reference_key,'current_condition_display':condition_text,'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'figure_sha256':hashlib.sha256(destination.read_bytes()).hexdigest()},indent=2,sort_keys=True)+'\n')
    destination.with_suffix('.caption.tex').write_text('The grader card separates ordinary-sampling errors from adaptive security claims. Discovery estimates concern accepted-but-wrong programs under the specified sampler. The discovery axis starts at zero and its displayed upper limit is explicit; recorded intervals and missing-data bounds use different marks. Conditional rejection uses oracle-passing sampled programs as its denominator; original-condition canonical-reference checks are reported separately and do not estimate rejection among arbitrary correct programs. Current runtime limits and host identity are printed when supplied. Unavailable fields are not zero estimates, and the revisit date is administrative.\n')
    return chart_metadata


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('card',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();render(args.card,args.output)
