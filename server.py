import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    logger.info(f"Client connected {addr}")
    
    while True:
        data = await reader.read(100)
        if not data:
            break
        
        try:
            message = data.decode()
            logger.info(f"Received {message} from {addr}")

            writer.write(data)
            await writer.drain()
        
        except UnicodeDecodeError:
            logger.warning(f"Received non-UTF-8 data from {addr}")
            break

    logger.info(f"Client disconnected: {addr}")
    writer.close()
    await writer.wait_closed()

async def run_server():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8080)
    addr = server.sockets[0].getsockname()
    logger.info(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(run_server())
