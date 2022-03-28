# WS server example

import asyncio
import websockets
import picamera
import dotenv

print('Initialising websocket server (cam 2)')
env_path = '/home/pi/camcheck/.env'
keys = dotenv.Dotenv(env_path)
WS_SERVER = keys['WS_SERVER']
WS_PORT = keys['WS_PORT']


cam = picamera.PiCamera()
cam.resolution = (640, 480)
cam.rotation = 180
cam.start_preview()

# def record(cam, nsec=10):
#     cam.start_recording('my_video.h264')
#     cam.wait_recording(nsec)
#     cam.stop_recording()


async def caputure(websocket, nsec=20):
    import base64
    name = await websocket.recv()

    if name == 'capture':
        print('start capturing')
        await websocket.send('ok')

        # start camera and capture
        cam.start_recording('my_video.h264')
        cam.wait_recording(nsec)
        cam.stop_recording()
        print('recording done')

    if name == 'retrieve':
        print('encoding and sending')
        # send capture file as binary
        vid = base64.b64encode(open("my_video.h264", "rb").read())
        await websocket.send(vid)
        print('done')

start_server = websockets.serve(caputure, WS_SERVER, WS_PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()