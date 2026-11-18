from copy import deepcopy
import pytest
from src.evaluation.skin_patch_review import validate_export, rasterize, valid_polygon


def fixture():
    manifest={'rows':[dict(review_id='one',image_sha256='b'*64,width=10,height=10)]}
    value=dict(schema_version='truehue_skin_patch_review_v1',manifest_sha256='a'*64,reviewer='fixture',draft=False,
        rows=[dict(review_id='one',image_sha256='b'*64,status='marked',notes='',polygons=[[[1,1],[3,1],[3,3],[1,3]]])])
    return value,manifest


def test_rectangle_boundary_and_union():
    v,m=fixture();rows=validate_export(v,m,'a'*64)
    mask=rasterize(rows[0]['polygons']*2,10,10)
    assert (mask>0).sum()==9 and mask[1,1] and mask[3,3] and not mask[0,0]


@pytest.mark.parametrize('p', [[[1,1],[4,4],[1,4],[4,1]], [[1,1],[2,2],[3,3]],
    [[True,1],[3,1],[3,3]], [[1,1],[3,1],[10,3]], [[1,1],[3,1],[3,3],[1,1]]])
def test_invalid_geometry(p):
    assert not valid_polygon(p,10,10)
    with pytest.raises(ValueError):rasterize([p],10,10)


@pytest.mark.parametrize('kind', ['draft','manifest','image','reviewer','duplicate','unknown','empty','unavailable'])
def test_strict_import(kind):
    v,m=fixture()
    if kind=='draft':v['draft']=True
    elif kind=='manifest':v['manifest_sha256']='c'*64
    elif kind=='image':v['rows'][0]['image_sha256']='c'*64
    elif kind=='reviewer':v['reviewer']=' '
    elif kind=='duplicate':v['rows'].append(deepcopy(v['rows'][0]))
    elif kind=='unknown':v['rows'][0]['review_id']='other'
    elif kind=='empty':v['rows'][0]['polygons']=[]
    elif kind=='unavailable':v['rows'][0]['status']='unavailable'
    with pytest.raises(ValueError):validate_export(v,m,'a'*64)


def test_unavailable_remains_empty():
    v,m=fixture();v['rows'][0].update(status='unavailable',notes='Too dark',polygons=[])
    assert validate_export(v,m,'a'*64)[0]['status']=='unavailable'
    assert not rasterize([],10,10).any()
