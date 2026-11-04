"""Isolated dense face-parser diagnostics; not imported by runtime masking."""
import cv2
import numpy as np

LABELS=('background','skin','left_brow','right_brow','left_eye','right_eye',
        'glasses','left_ear','right_ear','earring','nose','mouth','upper_lip',
        'lower_lip','neck','necklace','clothes','hair','hat')


def preprocess(image):
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
        raise ValueError('Nonempty uint8 BGR image required')
    rgb=cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),(512,512),interpolation=cv2.INTER_LINEAR)
    normalized=(rgb.astype(np.float32)/255-np.array([.485,.456,.406],np.float32))/np.array([.229,.224,.225],np.float32)
    return np.ascontiguousarray(normalized.transpose(2,0,1)[None])


def decode(logits,width,height):
    if logits.ndim!=4 or logits.shape[:2]!=(1,19) or not np.isfinite(logits).all():
        raise ValueError('Expected finite 1x19xHxW class logits')
    categories=np.argmax(logits[0],axis=0).astype(np.uint8)
    return cv2.resize(categories,(width,height),interpolation=cv2.INTER_NEAREST)


def facial_skin(categories):
    if categories.dtype!=np.uint8 or categories.ndim!=2 or not categories.size or (categories>18).any():
        raise ValueError('Native uint8 categories 0..18 required')
    return (categories==1)|(categories==10)


class DenseFaceParser:
    def __init__(self,path):
        self.net=cv2.dnn.readNetFromONNX(str(path))
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        if 'output' not in self.net.getUnconnectedOutLayersNames():
            raise ValueError('Published primary output not found')

    def categories_bgr(self,image):
        tensor=preprocess(image)
        self.net.setInput(tensor)
        logits=self.net.forward('output')
        if logits.shape!=(1,19,512,512):raise ValueError('Unexpected published output shape')
        return decode(logits,image.shape[1],image.shape[0])
