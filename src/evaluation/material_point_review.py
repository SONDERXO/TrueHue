"""Validate human point labels and score development-only mask observations."""

LABELS = ('skin','hair','paint','other','unsure')


def validate_labels(manifest, payload, manifest_sha256):
    if payload.get('draft',False):
        raise ValueError('Complete the review and save final labels before scoring')
    if payload.get('schema_version') != 'material_point_labels_v1' or payload.get('manifest_sha256') != manifest_sha256:
        raise ValueError('Labels do not match the review manifest')
    if not str(payload.get('reviewer','')).strip():
        raise ValueError('Reviewer name or initials required')
    expected = {p['point_id'] for p in manifest['points']}
    labels = payload.get('labels',[])
    if len(labels) != len(expected) or {r.get('point_id') for r in labels} != expected:
        raise ValueError('Exactly one label per manifest point required')
    if any(r.get('label') not in LABELS for r in labels):
        raise ValueError('Unknown material label')
    return {r['point_id']:r['label'] for r in labels}


def score_points(observations, labels):
    """Point counts, not image-area accuracy; unavailable observations stay visible."""
    results = []
    keys = sorted({(r['variant'],r['method']) for r in observations})
    for variant,method in keys:
        group = [r for r in observations if r['variant']==variant and r['method']==method]
        tp=fp=tn=fn=uncertain=unavailable=0
        categories = {label:dict(available=0,selected=0,unavailable=0) for label in LABELS}
        for row in group:
            label = labels[row['point_id']]
            if label=='unsure': uncertain += 1
            if row['selected'] is None:
                unavailable += 1; categories[label]['unavailable'] += 1
                continue
            if not isinstance(row['selected'],bool): raise ValueError('Selection must be boolean or unavailable')
            categories[label]['available'] += 1
            categories[label]['selected'] += int(row['selected'])
            if label=='unsure': continue
            if label=='skin':
                if row['selected']: tp += 1
                else: fn += 1
            elif row['selected']: fp += 1
            else: tn += 1
        results.append(dict(variant=variant,method=method,attempted_points=len(group),
            unavailable_points=unavailable,unsure_points=uncertain,tp=tp,fp=fp,tn=tn,fn=fn,
            skin_recall=tp/(tp+fn) if tp+fn else None,
            selected_point_precision=tp/(tp+fp) if tp+fp else None,
            non_skin_selection_rate=fp/(fp+tn) if fp+tn else None,by_material=categories))
    return results
