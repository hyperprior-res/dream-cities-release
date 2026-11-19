"""Render scheduled live events without treating them as settlement dates."""
import argparse
from collections import Counter, defaultdict
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_style import apply, save, TEXT_IN, RED, BLUE, INK, GREY, PALE
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle


LABELS = {
    'us-general-election-2026': 'US general election',
    'uk-budget-2026-10': 'UK budget',
    'pce-2026-09': 'PCE release',
    'ppi-2026-10': 'PPI release',
    'cpi-2026-10': 'CPI release',
    'fomc-2026-10': 'FOMC decision',
    'employment-2026-10': 'Employment release',
}


def render(source, destination):
    source, destination = Path(source), Path(destination)
    rows = [json.loads(line) for line in source.read_text().splitlines() if line.strip()]
    if not rows or len({row['question_id'] for row in rows}) != len(rows):
        raise ValueError('The live batch must contain distinct question records')
    groups = defaultdict(list)
    for row in rows:
        event = date.fromisoformat(row['scheduled_event_date'])
        groups[row['superfamily_id']].append((event, row))
    ordered = sorted(groups, key=lambda key: (-len(groups[key]), min(x[0] for x in groups[key]), key))
    unknown = sum(row.get('platform_settlement_date') is None for row in rows)
    expected_unknown = sum(row.get('expected_resolution_date') is None for row in rows)
    dates = [x[0] for group in groups.values() for x in group]
    start, end = min(dates) - timedelta(days=2), max(dates) + timedelta(days=2)
    apply()
    fig=plt.figure(figsize=(TEXT_IN,3.85))
    fig.text(.02,.965,'The live batch concentrates questions in shared scheduled events',fontsize=9,weight='bold',va='top')
    fig.text(.02,.895,f'{len(rows):,} questions · {len(groups)} broad event groups · no live outcome results',fontsize=7.5,color=GREY)
    counts_ax=fig.add_axes([.265,.225,.205,.57]);calendar=fig.add_axes([.60,.225,.365,.57],sharey=counts_ax)
    maximum=max(len(group) for group in groups.values())
    counts_ax.set(xlim=(0,maximum*1.22),ylim=(len(ordered)-.4,-.6),yticks=range(len(ordered)),
                  yticklabels=[LABELS.get(key,key.replace('-',' ')) for key in ordered])
    counts_ax.tick_params(axis='y',length=0,pad=9,labelsize=7.6)
    for y,key in enumerate(ordered):
        colour=RED if key=='us-general-election-2026' else BLUE
        number=len(groups[key]);counts_ax.barh(y,number,height=.22,color=colour,lw=0,zorder=2)
        counts_ax.text(number+maximum*.035,y,f'{number:,}',fontsize=7.3,color=colour,va='center')
        dates_for_group=Counter(event for event,_ in groups[key])
        for event,count in sorted(dates_for_group.items()):
            xx=mdates.date2num(event);calendar.plot(xx,y,'o',ms=4,color=colour,zorder=3)
            label=f'{event:%d %b}' if len(dates_for_group)==1 else f'{event:%d %b} ({count})'
            left=(end-event).days>3
            calendar.annotate(label,(xx,y),xytext=(7 if left else -7,0),textcoords='offset points',
                              ha='left' if left else 'right',va='center',fontsize=7.3,color=colour,
                              bbox={'facecolor':'white','edgecolor':'none','pad':.8})
        for axis in (counts_ax,calendar):axis.axhline(y,color='#E7E2DA',lw=.55,zorder=0)
    calendar.set_xlim(start,end);calendar.tick_params(axis='y',left=False,labelleft=False)
    calendar.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    calendar.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    calendar.grid(axis='x',color='#D9D2C8',lw=.55,zorder=0)
    counts_ax.set_xticks([0,maximum/2,maximum]);counts_ax.set_xlabel('Questions',fontsize=7.5)
    years=sorted({event.year for event in dates})
    date_label='Scheduled event date'+(' ('+str(years[0])+')' if len(years)==1 else '')
    calendar.set_xlabel(date_label,fontsize=7.5)
    for axis in (counts_ax,calendar):
        axis.spines[['top','right','left']].set_visible(False);axis.tick_params(axis='x',labelsize=7,length=2.3,width=.55,pad=6)
    fig.text(.265,.832,'Question concentration',fontsize=8,weight='bold')
    fig.text(.60,.832,'Calendar, not settlement',fontsize=8,weight='bold')
    fig.text(.02,.105,f'Settlement date unavailable for {unknown:,} of {len(rows):,} questions.',fontsize=7.5,color=INK)
    fig.text(.02,.055,'Question counts are not independent events; scoring uses the broad event groups by default.',fontsize=7.1,color=GREY)
    fig.text(.02,.015,'Scheduled dates do not promise settlement: certification, disputes or postponement can delay resolution.',fontsize=7.1,color=GREY)
    destination.parent.mkdir(parents=True, exist_ok=True)
    save(fig, destination)
    plt.close(fig)
    provenance = {
        'source_file': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'question_count': len(rows), 'superfamily_count': len(groups),
        'superfamily_counts': {key: len(groups[key]) for key in ordered},
        'scheduled_event_counts': dict(sorted(Counter(x.isoformat() for x in dates).items())),
        'unknown_platform_settlement_count': unknown, 'unknown_expected_resolution_count': expected_unknown,
        'date_interpretation': 'Scheduled event dates only. Platform settlement dates are distinct and may be unavailable.',
        'dependence': 'The US election questions share one superfamily and are not independent events.',
        'figure_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    destination.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2, sort_keys=True) + '\n')
    destination.with_suffix('.caption.tex').write_text(
        'The live batch is concentrated in a shared election event. '
        'Rows group questions by broad event group; labels give question counts and scheduled event dates. '
        'These dates are distinct from platform settlement dates, which are unavailable at capture. '
        'Election certification can occur after the vote. No live outcome results are shown.\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('questions', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    render(args.questions, args.output)
