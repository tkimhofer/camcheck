import asyncio
import dotenv
env_path = '/home/pi/camcheck/.env'
keys = dotenv.Dotenv(env_path)
WS_SERVER = keys['WS_SERVER']
WS_PORT = keys['WS_PORT']


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        WS_SERVER, WS_PORT)

    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

asyncio.run(tcp_echo_client('send_stream'))