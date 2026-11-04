"""Explicit TrueHue adaptation: MediaPipe anchors into FaceOcc POS alignment."""
import cv2
import numpy as np
from src.skin_masking.faceocc_coordinates import alignment_matrix

VERSION='faceocc_mediapipe_five_anchor_bridge_v1'
# Fixed semantic correspondence, not the upstream 3DDFA landmark generator.
ANCHORS=((33,133),(362,263),(1,),(61,),(291,))


def five_anchors(landmarks):
    points=np.asarray(landmarks,dtype=np.float64)
    if points.ndim!=2 or points.shape[0]<468 or points.shape[1]<2 or not np.isfinite(points).all():
        raise ValueError('Finite complete MediaPipe landmarks required')
    anchors=np.array([points[list(indices),:2].mean(axis=0) for indices in ANCHORS])
    if np.linalg.norm(anchors[0]-anchors[1])<1 or np.linalg.norm(anchors[3]-anchors[4])<1:
        raise ValueError('Degenerate eye or mouth anchor geometry')
    return anchors


def template_five(template68):
    template=np.asarray(template68,dtype=np.float64)
    if template.shape!=(68,3) or not np.isfinite(template).all():
        raise ValueError('Pinned source68x3 template required')
    # Exact upstream reduction from its 68-point template.
    return np.stack((template[[36,39]].mean(axis=0),template[[42,45]].mean(axis=0),
                     template[30],template[48],template[54]))


def align_input(image,landmarks,template68):
    if not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
        raise ValueError('Nonempty uint8 BGR image required')
    anchors=five_anchors(landmarks)
    matrix=alignment_matrix(anchors,template_five(template68),image.shape[0])
    aligned=cv2.warpAffine(image,matrix,(256,256),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    # Preserve the publisher's border-blur construction, including integer casts.
    h,w=image.shape[:2]
    corners=(np.array([[0,0,1],[w-1,h-1,1]])@matrix.T).astype(np.int32)
    left=max(int(corners[0,0]),0);top=max(int(corners[0,1]),0)
    right=min(int(corners[1,0]),255);bottom=min(int(corners[1,1]),255)
    # A wholly out-of-frame projection has no meaningful aligned input.
    if left>=256 or top>=256 or right<0 or bottom<0:
        raise ValueError('Face alignment has no source overlap')
    border=np.zeros((256,256,1),np.float64)
    border[:top]=1;border[bottom:]=1;border[:,:left]=1;border[:,right:]=1
    aligned=(aligned.astype(np.float32)*(1-border)+cv2.blur(aligned,(10,10))*border).astype(np.uint8)
    transformed=np.column_stack((anchors,np.ones(5)))@matrix.T
    inverse=cv2.invertAffineTransform(matrix)
    restored=np.column_stack((transformed,np.ones(5)))@inverse.T
    if not np.allclose(restored,anchors,atol=1e-8):raise ValueError('Anchor coordinate replay failed')
    return aligned,matrix,dict(version=VERSION,anchors_xy=anchors.tolist(),
        aligned_anchors_xy=transformed.tolist(),inverse_max_error=float(np.abs(restored-anchors).max()),
        upstream_landmark_equivalence=False)
