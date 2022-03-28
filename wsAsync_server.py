# WS server example

import asyncio
import websockets
import picamera

serverIP = '10.0.0.42'
port = 8765
cam = picamera.PiCamera()
cam.rotation = 180

async def caputure(websocket, nsec=10):
    import base64
    name = await websocket.recv()

    if name == 'capture':
        print('start capturing')
        # start camera and capture
        cam.resolution = (640, 480)
        cam.start_recording('my_video.h264')
        cam.wait_recording(nsec)
        cam.stop_recording()
        print('encoding')
        # send capture file as binary
        vid = base64.b64encode(open("my_video.h264", "rb").read())
        print('sending')
        await websocket.send(vid)
        print('done')

start_server = websockets.serve(caputure, serverIP, port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()