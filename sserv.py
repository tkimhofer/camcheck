import asyncio
import picamera
import io
import base64
import dotenv

env_path = '/home/pi/camcheck/.env'
keys = dotenv.Dotenv(env_path)
WS_SERVER = keys['WS_SERVER']
WS_PORT = keys['WS_PORT']


cam = picamera.PiCamera()
cam.resolution = (640, 480)
cam.rotation = 180
cam.start_preview()

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")
    if message == 'send_stream':
        sio = io.BytesIO()  # for Python3
        while 1 > 0:
            cam.capture(sio, "jpeg", use_video_port=True)
            writer.write(base64.b64encode(sio.getvalue()))
        #await writer.drain()
    else:
        print(f"Send: {message!r}")
        writer.write(data)
        await writer.drain()

    print("Close the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(
        handle_echo, WS_SERVER, WS_PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())