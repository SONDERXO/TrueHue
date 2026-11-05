"""Export fixed diagnostic findings/CSV without new fits or image inference."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'outputs/ffhq_correction_targets_v1'
OUT=ROOT/'outputs/ffhq_correction_targets_assessment_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
NOTES={
 '54632':'Core board close to original; stress under has pale/posterised appearance and magenta remnants around dark features/beard.',
 '39568':'Core board close to original; stress under has very dark eye/mouth regions and bright yellow/pale surrounding skin.',
 '29617':'Core board close to original; stress under shows magenta/dark lower-face patches; sunglasses/hand protections retained.',
 '29863':'Core board close to original; stress under has severe red/black posterisation and lost shadow detail; head covering protected.',
 '16061':'Core board close to original through clear lenses; stress under leaves mouth/lip colour artifacts and uneven brightening.',
 '52445':'Core board close to original; stress under retains eye/mouth colour artifacts and brighter cheeks; neck remains absent.',
 '32685':'Core board close to original; stress under shows lip/eye artifacts; partial neck/lighting issues not resolved.',
 '53146':'Core board close to original; stress under leaves strong eye/mouth darkening and washed bright areas.',
 '48879':'Core board close to original; stress under leaves dark eye/mouth remnants and brightened face; hair boundary uncertainty retained.',
 '49131':'Core board close to original; stress under leaves black eye/jaw patches and blocky colour transitions.',
 '59807':'Core board close to original with clear-lens correction; stress under shows eye/mouth/neck posterisation; microphone protected.',
 '46795':'Core board close to original; stress under leaves severe magenta/dark patches and flattened lower-face transitions.'}


def main():
    if OUT.exists():raise FileExistsError(OUT)
    manifest=read(PARENT/'sha256.json');inputs=read(PARENT/'plan.json')['input_sha256']
    assert all(sha(PARENT/p)==h for p,h in manifest.items())
    assert all(sha(p)==h for p,h in inputs.items())
    result=read(PARENT/'results.json');rows=[]
    for r in result['records']:
        rows.append(dict(source_id=r['source_id'],case_id=r['case']['id'],layer=r['case']['layer'],
            status=r['status'],severity_preset='medium',severity_basis='common_engineering_NOT_MST',
            input_MAE=r['input_metrics']['rgb8_mae_codes'],output_MAE=r.get('output_metrics',{}).get('rgb8_mae_codes'),
            input_deltaE00=r['input_metrics']['relative_deltaE00_mean'],output_deltaE00=r.get('output_metrics',{}).get('relative_deltaE00_mean'),
            forward_clipped_channels=r['recipe']['clipped_channel_samples'],
            fit_status=r['fit']['status'],training_admitted=False,MST=None))
    OUT.mkdir()
    with (OUT/'cases.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    with (OUT/'cases.csv').open(newline='',encoding='utf-8') as stream:csvrows=list(csv.DictReader(stream))
    assert len(csvrows)==168
    assert all(float(a['input_MAE'])==b['input_MAE'] and float(a['output_MAE'])==b['output_MAE'] and a['source_id']==b['source_id'] for a,b in zip(csvrows,rows))
    regressions=[r for r in rows if r['output_deltaE00'] is not None and r['output_deltaE00']>r['input_deltaE00']]
    assessment=dict(observer='assistant',inspection='predeclared_combined_cool_under_and_stress_combined_under_all12_at256px',
        inspected_boards=24,not_all168_visually_reviewed=True,observations=NOTES,
        deltaE00_regressions=regressions,layers=result['layers'],parent_manifest_sha256=sha(PARENT/'sha256.json'),
        source_script_sha256=sha(Path(__file__)),new_fits=0,new_inference=0,admissions=0,
        original_source_and_historical_hashes_unchanged=True,case_csv_JSON_parity=True)
    (OUT/'assessment.json').write_text(json.dumps(assessment,indent=2),encoding='utf-8')
    assert all(sha(PARENT/p)==h for p,h in manifest.items()) and all(sha(p)==h for p,h in inputs.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2))
    print('168 CSV/JSON rows verified;24 assistant boards recorded;4 retained deltaE regressions')


if __name__=='__main__':main()
