"""Source/annotation feasibility only: no image reads, model imports or fitting."""
import bisect
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/portrait_exposure_prior_review_v1'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((OUT / 'cache_sources.json').read_text(encoding='utf-8'))
    receipts = []
    for item in manifest['files']:
        path = OUT / item['name']
        normalized = path.read_text(encoding='utf-8').replace('\r\n', '\n')
        # apply_patch caches normalized text; restore the fetched newline convention
        # only for pinned repository blobs, then prove exact Git blob identity.
        if item.get('blob'):
            if not item['source_final_newline']:
                normalized = normalized.removesuffix('\n')
            restored = normalized.replace('\n', '\r\n') if item['source_crlf'] else normalized
            data = restored.encode('utf-8')
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            assert len(data) == item['blob']['size'], (item['name'], len(data))
            assert blob == item['blob']['sha'], (item['name'], blob)
            path.write_bytes(data)
        else:
            data = path.read_bytes()
            blob = None
        receipts.append({'file': item['name'], 'bytes': len(data), 'sha256': sha256(data),
                         'git_blob_sha1': blob, 'repository_path': item['repository_path']})

    data = (OUT / 'Scores_Exposure.csv').read_bytes()
    rows = list(csv.DictReader(io.StringIO(data.decode('utf-8'), newline='')))
    scenes = defaultdict(list)
    invalid = []
    for index, row in enumerate(rows):
        vals = [float(row[k]) for k in ['JOD', 'CI LOW', 'CI HIGH', 'JOD STD']]
        score, low, high, std = vals
        if not all(math.isfinite(x) for x in vals) or not low <= score <= high or std < 0:
            invalid.append(index)
        else:
            scenes[row['SCENE IDX']].append((low, high, score))
    scene_counts = []
    for scene, records in sorted(scenes.items(), key=lambda x: int(x[0])):
        lows = sorted(x[0] for x in records)
        ordered_pairs = sum(len(lows) - bisect.bisect_right(lows, high)
                            for low, high, score in records)
        scene_counts.append({'scene_idx': int(scene), 'valid_rows': len(records),
                             'all_unordered_pairs': len(records) * (len(records) - 1) // 2,
                             'strict_nonoverlap_interval_pairs': ordered_pairs})
    tree = json.loads((OUT / 'tree.json').read_text(encoding='utf-8'))
    branch = json.loads((OUT / 'branch.json').read_text(encoding='utf-8'))
    releases = json.loads((OUT / 'releases.json').read_text(encoding='utf-8'))
    assert branch['commit']['sha'] == manifest['commit']
    assert tree['sha'] == manifest['commit'] and tree['truncated'] is False
    weights = [x for x in tree['tree'] if x['path'].lower().endswith(
        ('.pth', '.pt', '.pkl', '.ckpt', '.onnx', '.safetensors'))]
    report = {
        'review_date': '2026-11-16', 'commit': manifest['commit'],
        'exact_pinned_blob_checks_passed': True,
        'complete_tree_entries': len(tree['tree']), 'weight_entries': weights,
        'release_count': len(releases), 'public_score_rows': len(rows),
        'unique_image_paths': len({r['IMAGE PATH'] for r in rows}),
        'attributes': dict(Counter(r['ATTRIBUTE'] for r in rows)),
        'conditions': dict(Counter(r['CONDITION'] for r in rows)),
        'scene_count': len({r['SCENE IDX'] for r in rows}),
        'invalid_finite_ordered_interval_rows': invalid,
        'strict_nonoverlap_interval_pairs': sum(x['strict_nonoverlap_interval_pairs'] for x in scene_counts),
        'all_within_scene_unordered_pairs': sum(x['all_unordered_pairs'] for x in scene_counts),
        'scenes_with_at_least_one_strict_pair': sum(x['strict_nonoverlap_interval_pairs'] > 0 for x in scene_counts),
        'scenes': scene_counts, 'cache_files': receipts,
        'pixels_read': 0, 'portrait_features_extracted': 0, 'predictor_fits': 0,
        'correction_renders': 0, 'new_human_ratings': 0,
        'interpretation': 'Annotation/ranking feasibility only; no model or correction effectiveness measured.',
        'status': 'SOURCE_REVIEW_COMPLETE_NO_FIT_SELECTED',
    }
    (OUT / 'annotation_feasibility.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ['scenes', 'cache_files', 'weight_entries']}, indent=2))


if __name__ == '__main__':
    main()
