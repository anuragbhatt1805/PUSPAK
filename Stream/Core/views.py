from django.views.decorators import gzip
from django.http import HttpResponseServerError, StreamingHttpResponse
import cv2

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)  # 0 is for default camera
        (self.grabbed, self.frame) = self.video.read()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        (self.grabbed, self.frame) = self.video.read()
        if not self.grabbed:
            raise RuntimeError("Failed to grab frame")
        # You can process the frame here (e.g., resize, compress)
        self.frame = cv2.resize(self.frame, (640, 480))
        ret, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
def stream(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        print("Error streaming camera feed")
        return HttpResponseServerError("Failed to stream camera feed")

