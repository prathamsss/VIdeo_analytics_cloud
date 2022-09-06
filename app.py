# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
"""
Run a Flask REST API exposing a YOLOv5s model
"""

import os
import io

import torch
from flask import Flask, request
from PIL import Image

app = Flask(__name__)
DETECTION_URL = "/get-prediction"
port = 5000
yolo_model_size = "yolov5s"
# Fix known issue urllib.error.HTTPError 403: rate
# limit exceeded https://github.com/ultralytics/yolov5/pull/7210
torch.hub._validate_not_a_forked_repo = lambda a, b, c: True


model = torch.hub.load("ultralytics/yolov5",
                       yolo_model_size)  # No force_reload to re-cache
model.conf = 0.50
model.iou = 0.45
# filter by list of classes ID

@app.route(DETECTION_URL, methods=["POST"])
def predict():
    """
    Post request method which does inference on
    given bytes of image. Needs to POST image bytes for HTTP request.

    :returns: Json containing details in YOLO style.
    """
    if request.method != "POST":
        return

    # Get data & convert it to PIL instance,
    # then send to model inference
    im_bytes = request.data
    input_img = Image.open(io.BytesIO(im_bytes))
    # reduce size=320 for faster inference
    results = model(input_img, size=640)
    return results.pandas().xyxy[0].to_json(orient="records")


if __name__ == "__main__":

    # debug=True causes Restarting with stat
    app.run(host="0.0.0.0", port=port)