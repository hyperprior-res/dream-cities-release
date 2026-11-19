"""Export a deterministic local resource ZIP from a verified Tectonic cache."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def build(cache, manifest, output):
    cache, manifest, output = map(Path, (cache, manifest, output))
    resources = {}
    for line in manifest.read_text().splitlines():
        name, size, digest = line.split()
        if size == '-1':
            continue
        if Path(name).name != name or name in ('', '.', '..', 'SHA256SUM'):
            raise ValueError('Unsafe or reserved resource name')
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid resource digest')
        data = (cache / 'files' / digest[:2] / digest[2:]).read_bytes()
        if len(data) != int(size) or hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('Cached resource does not match its manifest: ' + name)
        if name in resources and resources[name] != data:
            raise ValueError('Conflicting cached resource: ' + name)
        resources[name] = data
    if not resources:
        raise ValueError('The cache manifest has no resources')
    filelist = ''.join(name + ' ' + hashlib.sha256(data).hexdigest() + '\n'
                       for name, data in sorted(resources.items()))
    identity = hashlib.sha256(filelist.encode()).hexdigest()
    entries = dict(resources)
    entries['SHA256SUM'] = (identity + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w') as archive:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    report = {'source_manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
              'entries': len(resources), 'zip_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'identity_sha256': identity, 'partial_bundle': True,
              'network_used': False, 'file_sha256': {
                  name: hashlib.sha256(data).hexdigest() for name, data in sorted(resources.items())}}
    output.with_suffix('.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.cache, args.manifest, args.output)
    print(json.dumps({key: result[key] for key in ('entries', 'zip_sha256', 'identity_sha256')}))
