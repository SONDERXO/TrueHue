"""Freeze actual saved rows for a proposed exploratory fit; never fits/admit."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.ita_estimation.contextual_mst_experiment import FEATURES
PARENT=ROOT/'outputs/stellenbosch_new_subjects_v1'
OUT=ROOT/'outputs/exploratory_real_mst_preparation_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    bindings={str(PARENT/p):h for p,h in json.loads((PARENT/'sha256.json').read_text()).items()}
    for rel in ['scripts/478_prepare_exploratory_mst_rows.py','docs/exploratory-real-mst-protocol-2026-11-06.md']:
        bindings[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(Path(p))==h for p,h in bindings.items())
    rows=[]
    for r in json.loads((PARENT/'results_PRIVATE.json').read_text())['records']:
        available=r['status']=='success'
        assert r['calibration_admitted'] is False and r['training_admitted'] is False
        rows.append(dict(case_id=r['case_id'],subject_id=r['subject_key'],condition=r['condition'],
            source_mst_exact_decimal=r['source_mst_exact_decimal'],status='available' if available else 'unavailable',
            features={k:r['measurement_report']['features'][k] for k in FEATURES} if available else None,
            reason=None if available else r['reason'],calibration_admitted=False,training_admitted=False,
            actual_skin_validity='unverified',source_sha256=r['source_sha256']))
    assert len(rows)==30 and len({r['subject_id'] for r in rows})==10
    assert sum(r['status']=='available' for r in rows)==29
    OUT.mkdir(parents=True)
    summary=dict(status='prepared_not_fitted',attempts=30,available=29,unavailable=1,publisher_keys=10,
        real_fits=0,admissions=0,requires_explicit_exploratory_choice=True)
    for name,v in [('rows_PRIVATE.json',rows),('summary.json',summary),('input_sha256_PRIVATE.json',bindings)]:
        (OUT/name).write_text(json.dumps(v,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()},indent=2),encoding='utf-8')
    print(json.dumps(summary))


if __name__=='__main__':main()
