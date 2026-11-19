"""Render one actual question record; no placeholder statistics or generated data."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import textwrap
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_style import apply, save, TEXT_IN, RED, BLUE, INK, GREY, PALE
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def date(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime('%d %b %Y')


def render(row, destination, source_path=None):
    required = ['question_id', 'question', 'source', 'category', 'family_id',
                'created_ms', 'close_ms', 'resolved_ms', 'probability_creation',
                'probability_lead', 'initial_quote_ms', 'lead_quote_ms',
                'lead_target_ms', 'text_capture_utc', 'source_sha256']
    absent = [key for key in required if key not in row]
    if absent:
        raise ValueError('Missing card fields: ' + ', '.join(absent))
    for key in ('probability_creation','probability_lead'):
        if type(row[key]) not in (int,float) or not 0<=row[key]<=1:
            raise ValueError('Probability outside the unit interval')
    source=row['source_sha256'].get('market.json')
    if not source:
        raise ValueError('The market source hash is required')
    apply()
    fig=plt.figure(figsize=(TEXT_IN,4.05))
    ax=fig.add_axes([.015,.015,.97,.97]);ax.set(xlim=(0,100),ylim=(0,100));ax.axis('off')
    ax.text(0,98,'A question record separates model input from comparison metadata',fontsize=9,weight='bold',va='top',color=INK)
    ax.text(0,89,row['source'].capitalize()+'  /  '+row['category'],fontsize=7.3,color=GREY)
    ax.text(100,89,'Captured record, not an immutable historical title',fontsize=7.1,color=GREY,ha='right')
    ax.add_patch(Rectangle((0,60),100,24,facecolor=PALE,edgecolor='none'))
    ax.plot([0,0],[60,84],color=RED,lw=2.3,solid_capstyle='butt')
    ax.text(2.5,79.8,'SUPPLIED TO THE MODEL',fontsize=7.1,color=RED,weight='bold')
    title='\n'.join(textwrap.wrap(row['question'],width=93))
    if title.count('\n')>1:
        raise ValueError('Select a question with a shorter title for this compact card')
    ax.text(2.5,74.3,title,fontsize=9,weight='bold',color=INK,va='top',linespacing=1.15)
    ax.text(2.5,63.2,'Creation date: '+date(row['created_ms']),fontsize=7.5,color=INK)
    ax.text(0,54.5,'RETAINED FOR RETROSPECTIVE COMPARISON',fontsize=7.1,color=GREY,weight='bold')
    for x,label,stamp in [(0,'Scheduled close',row['close_ms']),(51,'Platform resolution',row['resolved_ms'])]:
        ax.text(x,48.4,label,fontsize=7.2,color=GREY)
        ax.text(x,42.3,date(stamp),fontsize=8.6,weight='bold',color=INK)
    ax.plot([0,100],[38.8,38.8],color='#D7D1C7',lw=.6)
    for x,label,probability,stamp in [(0,'Initial crowd quote',row['probability_creation'],row['initial_quote_ms']),
                                      (51,'Last recorded quote before lead cutoff',row['probability_lead'],row['lead_quote_ms'])]:
        ax.text(x,34,label,fontsize=7.2,color=GREY)
        ax.text(x,27.5,f'{probability:.1%}',fontsize=9,weight='bold',color=BLUE)
        ax.text(x+15,27.5,'Quote recorded '+date(stamp),fontsize=7.1,color=INK)
    ax.text(51,21.4,'Lead cutoff: '+date(row['lead_target_ms']),fontsize=7.1,color=GREY)
    ax.text(0,21.4,'Family: '+row['family_id'],fontsize=7.1,color=GREY)
    ax.plot([0,100],[17,17],color='#D7D1C7',lw=.6)
    ax.text(0,12.7,'Title capture: '+row['text_capture_utc'].split('T')[0]+' · Historical title immutability is not established.',fontsize=7.1,color=INK)
    ax.text(0,7.1,'Record ID: '+row['question_id'],fontsize=7,color=GREY)
    ax.text(0,1.5,'Source SHA-256: '+source[:24]+'… (shortened)',fontsize=7,color=GREY)
    ax.text(100,1.5,'No crowd quote was supplied in the historical prompt.',fontsize=7,color=INK,ha='right')
    destination = Path(destination); destination.parent.mkdir(parents=True, exist_ok=True)
    save(fig, destination)
    plt.close(fig)
    manifest = {'question_id': row['question_id'], 'title_sha256': hashlib.sha256(row['question'].encode()).hexdigest(),
                'source_sha256': row['source_sha256'], 'figure': destination.name,
                'figure_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if source_path is not None:
        manifest['question_file_sha256'] = hashlib.sha256(Path(source_path).read_bytes()).hexdigest()
    destination.with_suffix('.provenance.json').write_text(json.dumps(manifest, indent=2) + '\n')
    destination.with_suffix('.caption.tex').write_text(
        'The question record separates forecast inputs from retrospective comparison metadata. '
        'The model receives the title and creation date. Recorded market quotes carry their own '
        'timestamps, and the scheduled close is distinct from platform resolution. '
        'The source hash identifies the captured record; it does not establish historical title immutability.\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('questions', type=Path)
    parser.add_argument('--question-id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    matches = [json.loads(line) for line in args.questions.read_text().splitlines()
               if line.strip() and json.loads(line)['question_id'] == args.question_id]
    if len(matches) != 1:
        raise ValueError('Expected exactly one record with the requested ID')
    render(matches[0], args.output, args.questions)
