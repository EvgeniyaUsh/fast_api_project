import asyncio
import aiohttp

urls = [
    'https://example.com',
    'https://httpbin.org/status/200',
    'https://httpbin.org/status/404',
    'https://httpbin.org/status/500'
]

async def fetch_status(session, url):
    try:
        async with session.get(url) as response:
            return url, response.status
    except Exception as e:
        return url, f"Error: {e}"

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, url) for url in urls]
        
        # Обработка результатов по мере готовности
        for coro in asyncio.as_completed(tasks):
            url, status = await coro
            print(f"{url} -> {status}")

if __name__ == "__main__":
    asyncio.run(main())