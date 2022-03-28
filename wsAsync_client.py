import asyncio
# define client websocket
class CaptureWS:
    async def __aenter__(self, env_path = "/home/pi/camcheck/.env"):
        from websockets import connect
        import dotenv

        print('Initialising websocket cam 2')
        keys = dotenv.Dotenv(env_path)
        self.WS_SERVER = keys['WS_SERVER']
        self.WS_PORT = int(keys['WS_PORT'])
        self._conn = connect('ws://' + self.WS_SERVER + ':' + self.WS_PORT, max_size=3000000)
        self.websocket = await self._conn.__aenter__()
        return self
    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)
    async def send(self, message='capture'):
        await self.websocket.send(message)
    async def receive(self, fpath):
        import base64
        vid_bin = await self.websocket.recv()
        ts = base64.b64decode(vid_bin)  # decode
        fh = open(fpath, "wb")
        fh.write(ts)
        fh.close()
        print("cam2 video recorded (ws)")

async def main(fpath):
    async with CaptureWS() as cap:
        await cap.send()
        await cap.receive(fpath)
