import asyncio
import logging
from datetime import datetime
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conn = sqlite3.connect('requests.db')
cursor  = conn.cursor()
cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               client_addr TEXT, 
               message TEXT,
               recieved_at TEXT)
               ''')
conn.commit()

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    logger.info(f"Client connected {addr}")
    
    while True:
        data = await reader.read(100)
        if not data:
            break
        
        try:
            message = data.decode('utf-8')
            logger.info(f"Received {message} from {addr}")

            cursor.execute('''INSERT INTO requests (client_addr, message, recieved_at) VALUES (?, ?, ?)''', (str(addr), message, datetime.now().isoformat()))
            conn.commit()

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
    conn.close()
