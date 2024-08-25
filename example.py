import json
import asyncio
from AsyncCoinbaseAPI import AsyncCoinbaseAPI

# Load API credentials from JSON file
with open('cdp_api_key.json', 'r') as file:
    config = json.load(file)

API_KEY = config["name"]
API_SECRET = config["privateKey"]

if __name__ == "__main__":
    async def main():
        api = AsyncCoinbaseAPI(
            api_key=API_KEY,
            api_secret=API_SECRET,
            display_table=True
        )
        
        start = "1625097600"
        end = "1625184000"
        granularity = "FIVE_MINUTE"
        limit = 350

        tasks = []
        
        tasks.append(asyncio.create_task(api.async_call("get_candles", product_id="BTC-USD", start=start, end=end, granularity=granularity, limit=limit)))
        await asyncio.sleep(2)
        
        tasks.append(asyncio.create_task(api.async_call("get_candles", product_id="ETHUSD", start=start, end=end, granularity=granularity, limit=limit)))
        await asyncio.sleep(2)
        
        tasks.append(asyncio.create_task(api.async_call("get_candles", product_id="LTC-USD", start=start, end=end, granularity=granularity, limit=limit)))
        await asyncio.sleep(2)
        
        tasks.append(asyncio.create_task(api.async_call("get_candles", product_id="ADA-USD", start=start, end=end, granularity=granularity, limit=limit)))

        await asyncio.gather(*tasks)
        await asyncio.sleep(2)
        await api.close()

    asyncio.run(main())