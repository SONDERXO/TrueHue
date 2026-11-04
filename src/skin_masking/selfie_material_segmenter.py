"""Local MediaPipe multiclass segmentation for correction-only experiments."""
from pathlib import Path
import cv2
import numpy as np

LABELS=('background','hair','body-skin','face-skin','clothes','others')


def normalize_category_map(categories,image_shape):
    """Accept documented single-channel image representations without resizing."""
    category=np.asarray(categories)
    if category.ndim==3 and category.shape[2]==1: category=category[:,:,0]
    if category.shape!=tuple(image_shape[:2]) or category.dtype!=np.uint8:
        raise ValueError('Expected native-resolution uint8 category map')
    if (category>5).any(): raise ValueError('Unknown output category')
    return category.copy()


class SelfieMaterialSegmenter:
    def __init__(self,model_path):
        import mediapipe as mp
        self.mp=mp
        if not Path(model_path).is_file(): raise FileNotFoundError(model_path)
        options=mp.tasks.vision.ImageSegmenterOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            output_category_mask=True,output_confidence_masks=False)
        self.task=mp.tasks.vision.ImageSegmenter.create_from_options(options)
        if tuple(self.task.labels)!=LABELS:
            self.task.close();raise ValueError('Unexpected model category order')

    def categories_bgr(self,image_bgr):
        image=np.asarray(image_bgr)
        if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
            raise ValueError('Expected nonempty uint8 BGR image')
        rgb=np.ascontiguousarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
        result=self.task.segment(self.mp.Image(image_format=self.mp.ImageFormat.SRGB,data=rgb))
        if result.category_mask is None: raise ValueError('Segmentation returned no categories')
        return normalize_category_map(result.category_mask.numpy_view(),image.shape)

    def close(self): self.task.close()


def face_skin_support(categories,face_box,exclusion_crop):
    """Select face-skin argmax within the detected face, minus feature exclusions."""
    category=np.asarray(categories);excluded=np.asarray(exclusion_crop)
    if category.ndim!=2 or category.dtype!=np.uint8 or (category>5).any():
        raise ValueError('Expected 2D uint8 categories 0 through 5')
    x,y,w,h=face_box
    if any(not isinstance(v,(int,np.integer)) for v in face_box) or min(x,y)<0 or min(w,h)<=0 or x+w>category.shape[1] or y+h>category.shape[0]:
        raise ValueError('Invalid face box')
    if excluded.dtype!=bool or excluded.shape!=(h,w): raise ValueError('Invalid feature exclusions')
    mask=np.zeros(category.shape,bool)
    mask[y:y+h,x:x+w]=(category[y:y+h,x:x+w]==3)&~excluded
    return mask


def hair_veto_support(categories,material_support):
    """Only remove predicted hair; other material errors can remain."""
    category=np.asarray(categories);support=np.asarray(material_support)
    if category.dtype!=np.uint8 or category.ndim!=2 or (category>5).any():
        raise ValueError('Expected category map')
    if support.dtype!=bool or support.shape!=category.shape: raise ValueError('Expected matching boolean support')
    return support & (category!=1)
