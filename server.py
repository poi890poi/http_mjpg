import uuid
import time
import asyncio

import cv2
from turbojpeg import TurboJPEG
import numpy as np
import tornado.ioloop
import tornado.web
from tornado import web, iostream, gen


class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        
    async def get(self):
        boundary = '{}'.format(str(uuid.uuid4()))
        self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary={}'.format(boundary))
        boundary = ('--{}'.format(boundary)).encode()
        content_id = 0
        while True:
            try:
                now = time.time()
                img = (np.random.rand(480*3,640*3,3) * 255).astype('uint8')
                #retval, buf	= cv2.imencode('.jpg', img)
                #buf = buf.tobytes()
                jpeg = TurboJPEG()
                buf = jpeg.encode(img)
                #buf = ('Time: {}'.format(now)).encode() # For debug
                timestamp = str(now).encode()
                self.write(boundary)
                self.write(b'\n')
                self.write(b'Content-Type: image/jpeg\n')
                self.write(b'Content-Id: ')
                self.write(str(content_id).encode())
                self.write(b'\n')
                self.write(b'Content-Length: ')
                self.write(str(len(buf)).encode())
                self.write(b'\n')
                self.write(b'Content-Timestamp: ')
                self.write(timestamp)
                self.write(b'\n\n') # RFC1341 Boundary or headers are followed by double CRLF to mark the start of content.
                self.write(buf)
                self.write(b'\n')
                await self.flush()
                content_id += 1
            except iostream.StreamClosedError:
                break
            finally:
                await gen.sleep(0.001) # 1 ms
        print('FINALIZE')
        self.finish()
        
    def post(self):
        self.set_status(200)
        self.finish()

    def options(self):
        self.set_status(204)
        self.finish()


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    port = 8888
    app = make_app()
    app.listen(port)
    print('Video streaming at http://localhost:{}'.format(port))
    tornado.ioloop.IOLoop.current().start()