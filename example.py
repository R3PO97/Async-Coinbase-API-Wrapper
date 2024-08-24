import os
import asyncio
from dotenv import load_dotenv
from src.async_coinbase_api import AsyncCoinbaseAPI

load_dotenv()

API_KEY = os.getenv("COINBASE_API_KEY")
API_SECRET = os.getenv("COINBASE_API_SECRET")

if __name__ == "__main__":
    async def main():
        api = AsyncCoinbaseAPI(
            api_key=API_KEY,
            api_secret=API_SECRET,
            verbose=True
        )
        
        start = "1625097600"
        end = "1625184000"
        granularity = "FIVE_MINUTE"
        limit = 350

        tasks = []
        
        tasks.append(asyncio.create_task(api.async_call("get_candles", product_id="BTC-USD", start=start, end=end, granularity=granularity, limit=limit)))
        await asyncio.sleep(2)
        
        tasks.append(asyncio.create_task(api.async_call("get_candles", product_id="ETH-USD", start=start, end=end, granularity=granularity, limit=limit)))
        await asyncio.sleep(2)
        
        tasks.append(asyncio.create_task(api.async_call("get_candles", product_id="LTC-USD", start=start, end=end, granularity=granularity, limit=limit)))
        await asyncio.sleep(2)
        
        tasks.append(asyncio.create_task(api.async_call("get_candles", product_id="ADA-USD", start=start, end=end, granularity=granularity, limit=limit)))

        await asyncio.gather(*tasks)
        await asyncio.sleep(2)
        await api.close()

    asyncio.run(main())