"""Conservative image-level partitions; does not infer subject identity."""
import hashlib


def connected_groups(ids, links):
    parent={i:i for i in ids}
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    for a,b in links:
        ra,rb=root(a),root(b)
        parent[max(ra,rb)]=min(ra,rb)
    groups={}
    for i in sorted(ids):
        groups.setdefault(root(i),[]).append(i)
    return list(groups.values())


def allocate_group(ids, source_splits, exposed_ids, seed=42):
    """Retain original source boundaries and keep inspected IDs out of test."""
    splits={source_splits[i] for i in ids}
    if not splits <= {'train','validation'}:
        raise ValueError('Unknown original source split')
    if len(splits)>1:
        return 'quarantine_cross_source_split'
    if splits=={'validation'}:
        return 'development_validation' if set(ids)&set(exposed_ids) else 'reserved_test'
    key=f'{seed}:'+ '|'.join(sorted(ids))
    fraction=int(hashlib.sha256(key.encode()).hexdigest()[:16],16)/2**64
    return 'development_validation' if fraction<.2 else 'train'


def classify_pair(processing_status, clipped_pixel_count):
    """Primary technical set excludes failed inputs and irreversible clipping."""
    if processing_status!='success':
        return 'excluded_input_pipeline_failure'
    if clipped_pixel_count>0:
        return 'stress_only_clipped'
    return 'technical_candidate'
