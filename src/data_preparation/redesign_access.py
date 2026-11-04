"""Workflow guard for new training preparation; not an OS filesystem sandbox."""
from copy import deepcopy
from pathlib import PureWindowsPath


def training_candidate(image_id,manifest,policy):
    """Return only a declared training candidate without opening any image.

    Validation/test phases need separate deliberate activation. This guard is
    for new preparation callers; it does not retroactively restrict old scripts.
    """
    if policy.get('permitted_current_role')!='train' or policy.get('automatic_unlock') is not False:
        raise ValueError('Only explicitly locked training-preparation phase supported')
    if set(policy.get('locked_roles',[]))!={'development_validation','final_test'}:
        raise ValueError('Validation and final-test roles must remain locked')
    rows=manifest.get('selected')
    if not isinstance(rows,list) or any(not isinstance(r,dict) for r in rows):raise ValueError('Candidate manifest required')
    ids=[r.get('image_id') for r in rows]
    if any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)):raise ValueError('Unique candidate IDs required')
    selected=next((r for r in rows if r['image_id']==image_id),None)
    if selected is None:raise ValueError('ID is outside frozen candidate allocation')
    if selected.get('role')!='train':raise PermissionError('Validation/test candidate is locked against development preparation')
    if selected.get('original_split')!='train':raise ValueError('Original validation data cannot enter training')
    path=selected.get('relative_image_path')
    if not isinstance(path,str) or PureWindowsPath(path).is_absolute() or PureWindowsPath(path).drive or '..' in PureWindowsPath(path).parts:
        raise ValueError('Workspace-relative image path required')
    if selected.get('eligibility')!='unreviewed_candidate':raise ValueError('This entry point only handles unreviewed candidate preparation')
    return deepcopy(selected)
