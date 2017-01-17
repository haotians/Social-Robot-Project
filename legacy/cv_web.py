#!/usr/bin/env python
# Usage:
# 1. Install Python dependencies: cv2, flask. (wish that pip install works like a charm)
# 2. Run "python main.py".
# 3. Navigate the browser to the local web page.
from flask import Flask, render_template, Response

from legacy.CVDetect import FaceDetect

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def gen():
    cv_camera = FaceDetect()
    while True:
        frame = cv_camera.face_detection_web()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=True)
