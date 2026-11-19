"""Definition-only overview, with explicit validated production selection."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diagram_style import Diagram, RED, BLUE, INK, MUTED, RULE, RED_PALE, BLUE_PALE

REPO = Path(__file__).resolve().parents[3]


def bind_analysis(path):
    path=Path(path).resolve();raw=path.read_bytes();document=json.loads(raw)
    sys.path.insert(0,str(REPO/'hyperprior/p2-hackability-measured/code'))
    from analyse_execution_conditions import validate as validate_report
    from environment_replay_figures import validate as validate_replay
    validate_report(document);result=validate_replay(document)
    if document.get('synthetic_fixture'):raise ValueError('A synthetic document cannot select a production overview')
    if result['status']!='complete':raise ValueError('A complete paired replay is required for this overview')
    source=REPO/'hyperprior/p2-hackability-measured/code/analyse_execution_conditions.py'
    if document.get('provenance',{}).get('analysis_source_sha256',{}).get('p2-hackability-measured/code/analyse_execution_conditions.py')!=hashlib.sha256(source.read_bytes()).hexdigest():
        raise ValueError('Execution-report analysis source fingerprint differs')
    if not document['provenance'].get('raw_and_frozen_inputs_sha256'):raise ValueError('Execution-report input provenance is absent')
    return {'analysis_path':str(path),'analysis_sha256':hashlib.sha256(raw).hexdigest(),
            'phase':document['phase'],'replay_status':result['status'],
            'corrected_population_status':document['measurement_population']['status'],
            'corrected_population_reason':document['measurement_population']['reason'],
            'validation_sources_sha256':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest()for p in
                (source,source.with_name('environment_replay_figures.py'))}}


def render(output,*,production=False,analysis=None):
    output = Path(output).resolve()
    if production and analysis is None:raise ValueError('Production mode requires an execution-report analysis path')
    if not production and analysis is not None:raise ValueError('Candidate mode does not read an analysis file')
    binding=bind_analysis(analysis)if production else None
    if not production and not output.is_relative_to(REPO / '.research-run'):
        raise ValueError('The execution overview remains a candidate outside production')
    output.mkdir(parents=True, exist_ok=True)
    d = Diagram(282)
    d.heading('A', 'The same saved programs, paired by identity', 4)
    d.text(18, 19, 'Program bytes, task identities, tests and resource limits are held fixed', 'note', colour=MUTED)
    d.document(18, 58, 27, 36, INK)
    d.text(57, 60, 'Saved programs', 'title', bold=True)
    d.text(57, 75, 'Exact source hashes', 'note', colour=MUTED)
    d.text(18, 107, 'One fixed program population', 'note', colour=MUTED)
    d.line(158, 77, 172, 77, MUTED)
    d.line(172, 58, 172, 113, MUTED)
    d.arrow(172, 58, 187, 58, RED)
    d.arrow(172, 113, 187, 113, BLUE)
    for y, title, detail, colour, fill in [
        (43, 'Original local execution', 'Recorded local conditions', RED, RED_PALE),
        (98, 'Separate host-b replay', 'Recorded replay conditions', BLUE, BLUE_PALE),
    ]:
        d.rect(194, y, 132, 35, fill, edge='none')
        d.rule(194, y, 132, colour, 1.4)
        d.text(201, y+7, title, 'title', colour=colour, bold=True)
        d.text(201, y+22, detail, 'small', colour=MUTED)
    d.line(334, 58, 344, 58, RED)
    d.line(334, 113, 344, 113, BLUE)
    d.line(344, 58, 344, 113, MUTED)
    d.arrow(344, 85, 357, 85, INK)
    d.text(365, 53, 'Common assessment', 'title', bold=True)
    d.text(365, 70, 'The same six graders', 'body', colour=RED)
    d.text(365, 86, 'The same held-out oracle', 'body', colour=BLUE)
    d.text(365, 105, 'Paired verdict records', 'note', colour=MUTED)
    d.text(18, 146, 'Machine, operating system, time and load differ together; no hardware-only effect is identified.', 'note', colour=MUTED)
    d.rule(0, 164, d.width)
    d.heading('B', 'Compare verdicts on the same identities', 177)
    d.text(18, 194, 'Transitions', 'title', bold=True)
    d.text(18, 208, 'Agreement, changes and unavailable verdicts', 'note')
    d.text(264, 194, 'Accepted-but-wrong probability', 'title', bold=True)
    d.text(264, 209, r'$q=\Pr(G=1,\ O=0)$', 'body', colour=RED)
    d.text(264, 225, 'Signed contrast: replay minus original', 'note', colour=MUTED)
    d.rule(0, 243, d.width)
    d.text(3, 253, 'Separate question: unavailable', 'title', bold=True)
    d.text(190, 253, 'Full remeasurement and audit–optimisation prediction', 'body', colour=MUTED)
    d.text(190, 267, 'The paired execution comparison does not substitute for either.', 'small', colour=MUTED)
    destination = output / 'p2-execution-overview.pdf'
    d.finish(destination)
    planned = REPO / 'hyperprior/p2-hackability-measured/paper/figures/fig1-overview.pdf'
    preserved = output / 'p2-planned-study-overview.pdf'
    shutil.copyfile(planned, preserved)
    inputs = [Path(__file__), Path(__file__).resolve().parents[1]/'diagram_style.py',
              Path(__file__).resolve().parents[1]/'figure_style.py']
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    (output / 'execution-overview.provenance.json').write_text(json.dumps({
        'schema': 'hpr-execution-overview-v1', 'empirical_values_drawn': False,
        'production': production, 'analysis_binding':binding, 'minimum_font_pt': 7,
        'source_sha256': {str(path.relative_to(REPO)): digest(path) for path in inputs},
        'outputs': {path.name: digest(path) for path in (destination, preserved)},
        'preserved_planned_source': str(planned.relative_to(REPO)),
    }, indent=2, sort_keys=True)+'\n')
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--production',action='store_true')
    parser.add_argument('--analysis',type=Path)
    args=parser.parse_args()
    print(render(args.output_dir,production=args.production,analysis=args.analysis))
