"""Same native-grid comparison with only the frozen detector fallback changed."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/515_evaluate_input_derived_correction.py').read_text()
source=source.replace('outputs/input_derived_mask_check_v1','outputs/detector_appearance_merged_v1').replace('outputs/input_derived_correction_v1','outputs/detector_appearance_correction_v1')
source=source.replace("P/cid/'native_grid.png'","Path(r['artifact_root'])/'native_grid.png'")
source=source.replace('import json,hashlib,sys','import json,hashlib,sys,shutil')
source=source.replace("    OUT.mkdir();records=[];boards=[]", "    cached_package=ROOT/'outputs/input_derived_correction_v1'\n    cached={r['case_id']:r for r in read(cached_package/'results_PRIVATE.json')['records']}\n    bound.update({str(cached_package/n):h for n,h in read(cached_package/'sha256.json').items()})\n    bound[str(ROOT/'scripts/515_evaluate_input_derived_correction.py')]=sha(ROOT/'scripts/515_evaluate_input_derived_correction.py')\n    assert all(sha(Path(p))==h for p,h in bound.items())\n    OUT.mkdir();records=[];boards=[]")
source=source.replace("        image=rgb(Path(r['source_path']))", "        if not r['detector_fallback_target']:\n            shutil.copytree(cached_package/cid,folder,dirs_exist_ok=True)\n            records.append(cached[cid])\n            if r['recipe'] in ['clean','combined_cool_under','stress_combined_over']:boards.append(cid)\n            continue\n        image=rgb(Path(r['source_path']))")
exec(compile(source,str(ROOT/'scripts/515_evaluate_input_derived_correction.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
