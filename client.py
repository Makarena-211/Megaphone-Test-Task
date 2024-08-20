import asyncio
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def client_task(client_id):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8080)
    
    for i in range(5):
        message = f"Client {client_id} message {i + 1}"
        logger.info(f'Sending: {message}')
        writer.write(message.encode('utf-8'))
        await writer.drain()
        
        data = await reader.read(100)
        if data:
            logger.info(f'Received echo: {data.decode()}')
        else:
            logger.warning(f"No echo received for: {message}")
        
        await asyncio.sleep(random.uniform(5, 10))

    writer.close()
    await writer.wait_closed()
    logger.info(f'Client {client_id} finished')

async def main():
    client_tasks = [asyncio.create_task(client_task(i)) for i in range(10)]
    await asyncio.gather(*client_tasks)

if __name__ == '__main__':
    asyncio.run(main())
