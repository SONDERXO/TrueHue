"""Strict native-grid sparse-reference import, never dense ground truth/admission."""
from collections import Counter
LABELS={'skin','hair_or_beard','object_or_other','uncertain'}

def validate_export(value,manifest,identity):
    if not isinstance(value,dict) or set(value)!={'schema_version','manifest_sha256','reviewer','rows'} or value.get('schema_version')!='truehue_native_reference_points_v1' or value.get('manifest_sha256')!=identity:
        raise ValueError('Schema or exact manifest binding mismatch')
    if not isinstance(value.get('reviewer'),str) or not value['reviewer'].strip():raise ValueError('Reviewer identity/code required')
    expected={r['review_id']:r for r in manifest['rows']};rows=value.get('rows')
    if not isinstance(rows,list) or len(rows)!=len(expected):raise ValueError('All fixed review cases required')
    seen=set()
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'review_id','image_sha256','status','notes','points'} or not isinstance(row.get('review_id'),str) or row['review_id'] not in expected or row['review_id'] in seen:raise ValueError('Duplicate/unknown review case')
        key=row['review_id'];seen.add(key);bound=expected[key]
        if row.get('image_sha256')!=bound['image_sha256']:raise ValueError('Native image hash mismatch')
        if row.get('status') not in ['marked','cannot_judge'] or not isinstance(row.get('notes'),str):raise ValueError('Explicit status and notes required')
        points=row.get('points')
        if not isinstance(points,list) or len(points)>50:raise ValueError('At most50native points per image')
        coords=set();definite=0
        for point in points:
            if not isinstance(point,dict) or set(point)!={'x','y','label'} or not isinstance(point['label'],str) or point['label'] not in LABELS:raise ValueError('Native point schema/label invalid')
            x,y=point['x'],point['y']
            if type(x) is not int or type(y) is not int or not 0<=x<bound['width'] or not 0<=y<bound['height']:raise ValueError('Integer native coordinates inside image required')
            if (x,y) in coords:raise ValueError('Duplicate/contradictory pixel labels')
            coords.add((x,y));definite+=point['label']!='uncertain'
        if row['status']=='marked' and not definite:raise ValueError('Marked image needs at least one definite point')
        if row['status']=='cannot_judge' and (definite or not row['notes'].strip()):raise ValueError('Cannot-judge needs reason and no definite points')
    return rows

def compare_points(rows,native_predictions):
    """native_predictions maps review ID to binary native crop mask or None."""
    counts=Counter();details=[]
    for row in rows:
        counts['images']+=1;counts['cannot_judge_images']+=row['status']=='cannot_judge'
        prediction=native_predictions[row['review_id']]
        for point in row['points']:
            label=point['label'];counts['points']+=1;counts[label+'_points']+=1
            selected=None if prediction is None else bool(prediction[point['y'],point['x']])
            if label=='uncertain':counts['uncertain_excluded']+=1
            elif selected is None:counts['definite_unavailable']+=1
            else:
                name='skin' if label=='skin' else 'unwanted'
                counts[name+'_available']+=1;counts[name+'_selected']+=selected
            details.append(dict(review_id=row['review_id'],**point,predicted_selected=selected,admitted=False))
    summary=dict(counts)
    summary.update(skin_point_inclusion=counts['skin_selected']/counts['skin_available'] if counts['skin_available'] else None,
        unwanted_point_inclusion=counts['unwanted_selected']/counts['unwanted_available'] if counts['unwanted_available'] else None,
        segmentation_accuracy=False,calibration_admissions=0)
    return dict(summary=summary,points=details)
