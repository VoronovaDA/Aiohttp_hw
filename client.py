import asyncio

import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        # response = await session.post(
        #     "http://127.0.0.1:8080/ads/",
        #     json={"header": "test", "description": "text", "user_name": "user_1"},
        # )
        # data = await response.json()
        # print(data)

        # response = await session.get(
        #     "http://127.0.0.1:8080/ads/1/",
        # )
        # data = await response.json()
        # print(data)
        #
        # response = await session.patch(
        #     "http://127.0.0.1:8080/ads/1/", json={"description": "text5"}
        # )
        # data = await response.json()
        # print(data)
        #
        response = await session.delete(
            "http://127.0.0.1:8080/ads/1/",
        )
        data = await response.json()
        print(data)


asyncio.run(main())
