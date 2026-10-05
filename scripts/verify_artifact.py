#!/usr/bin/env python3
"""Read-only release checksums and optional exact upstream source verification."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

BASE = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream',type=Path,help='Optional separate AgentProtocols checkout')
    args = parser.parse_args()
    manifest = json.loads((BASE/'notes/publication_manifest.json').read_text())
    expected = manifest['release_file_sha256']
    missing,changed = [],[]
    for relative,sha in expected.items():
        path = BASE / relative
        if not path.is_file(): missing.append(relative)
        elif digest(path) != sha: changed.append(relative)
    if missing or changed:
        raise SystemExit(json.dumps({'missing':missing,'changed':changed},indent=2))
    print(f'PASS: {len(expected)} public release file hashes (manifest excluded from its own map).')
    if args.upstream:
        upstream = args.upstream.expanduser().resolve()
        head = subprocess.check_output(['git','-C',str(upstream),'rev-parse','HEAD'],text=True).strip()
        if head != manifest['baseline_commit']:
            raise SystemExit('Upstream HEAD differs from audited baseline.')
        source = json.loads((BASE/'results/raw/real_protocol_manifest.json').read_text())['source_sha256']
        mismatches = [r for r,sha in source.items() if not (upstream/r).is_file() or digest(upstream/r) != sha]
        if mismatches:
            raise SystemExit('Upstream source mismatch: '+', '.join(mismatches))
        print(f'PASS: upstream commit and {len(source)} audited source/config hashes.')

if __name__ == '__main__':
    main()
