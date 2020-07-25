import uuid
import time
import asyncio

import cv2
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
        boundary = '--{}'.format(str(uuid.uuid4()))
        self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary={}'.format(boundary))
        boundary = boundary.encode()
        content_id = 0
        while True:
            try:
                self.write(boundary)
                self.write(b'\n')
                self.write(b'Content-Type: text/plain\n')
                self.write(b'Content-Id: ')
                self.write(str(content_id).encode())
                self.write(b'\n\n')
                now = time.time()
                self.write(('Time: {}\n'.format(now)).encode())
                await self.flush()
                print(now)
                if content_id > 8: break
                content_id += 1
            except iostream.StreamClosedError:
                break
            finally:
                await gen.sleep(0.000000001) # 1 nanosecond
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