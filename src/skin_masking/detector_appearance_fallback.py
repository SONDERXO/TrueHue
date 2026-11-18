"""Single fixed recognition-copy retry for zero-face detections only."""
import hashlib
from src.skin_masking.segmentation_appearance_probe import parser_input

def detect_with_appearance_fallback(image,detect):
    original=detect(image)
    trace=dict(original_boxes=[list(map(int,b)) for b in original],original_input_sha256=hashlib.sha256(image.tobytes()).hexdigest(),fallback_attempted=False)
    if len(original)!=0:return original,trace
    enhanced=parser_input(image)
    boxes=detect(enhanced)
    trace.update(fallback_attempted=True,enhanced_boxes=[list(map(int,b)) for b in boxes],enhanced_input_sha256=hashlib.sha256(enhanced.tobytes()).hexdigest(),accepted=len(boxes)==1)
    return (boxes if len(boxes)==1 else []),trace
