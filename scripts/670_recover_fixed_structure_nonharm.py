"""Preserve and replay-check 665 partials, then execute its outstanding finalisation."""
from pathlib import Path
import hashlib
import json
import traceback

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/fixed_structure_nonharm_models_v1'

def main():
    source = ROOT / 'scripts/665_reassign_fixed_structure_nonharm.py'
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    partials = sorted(OUT.glob('*_PRIVATE.json'))
    assert len(partials) == 11
    assert not (OUT / 'models_PRIVATE.json').exists()
    receipt = OUT / 'recovery_PRIVATE.json'
    assert not receipt.exists()
    before = {str(p): sha(p) for p in partials}
    record = dict(partial_sha256=before, source_sha256=sha(source),
                  recovery_script_sha256=sha(Path(__file__)),
                  method='Replay 665 leaf reassignment in memory; require exact partial equality; preserve partials; run outstanding finalisation.',
                  process_check='Get-Process python* returned no processes before recovery',
                  new_split_fits=0, holdout_image_reads=0, completed=False)
    code = source.read_text()
    guard = "if OUT.exists():raise FileExistsError('Preserve completed/partial fits')"
    write = "(OUT/(f['held_key']+'_PRIVATE.json')).write_text(json.dumps(f,indent=2))"
    assert code.count(guard) == code.count(write) == 1
    code = code.replace(guard, "assert OUT.is_dir()")
    code = code.replace('OUT.mkdir();result=', 'result=')
    code = code.replace(write, "assert read(OUT/(f['held_key']+'_PRIVATE.json')) == f")
    namespace = {'__file__': str(source), '__name__': 'recovered_665'}
    try:
        exec(compile(code, str(source), 'exec'), namespace)
        namespace['main']()
        record['completed'] = True
    except Exception:
        record['failure'] = traceback.format_exc()
        raise
    finally:
        record['partials_unchanged'] = all(sha(Path(p)) == h for p, h in before.items())
        receipt.write_text(json.dumps(record, indent=2))
        assert record['partials_unchanged']

if __name__ == '__main__':
    main()
