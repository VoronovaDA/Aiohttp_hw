import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError

from models import Ads, Base, Session, engine

app = web.Application()


async def orm_cntx(app: web.Application):
    print("START")
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("SHUT DOWN")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request["session"] = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_cntx)
app.middlewares.append(session_middleware)


def get_http_error(http_error_class, message):
    return http_error_class(
        text=json.dumps({"error": message}), content_type="application/json"
    )


async def ads_get(ads_id: int, session: Session) -> Ads:
    ads = await session.get(Ads, ads_id)
    if ads is None:
        raise get_http_error(web.HTTPNotFound, "advertisement not found")
    return ads


class AdsView(web.View):
    @property
    def session(self) -> Session:
        return self.request["session"]

    @property
    def ads_id(self) -> int:
        return int(self.request.match_info["ads_id"])

    async def get(self):
        ads = await ads_get(self.ads_id, self.session)
        return web.json_response(
            {
                "id": ads.id,
                "header": ads.header,
                "description": ads.description,
                "user_name": ads.user_name,
                "creation_time": ads.creation_time.isoformat(),
            }
        )

    async def post(self):
        json_data = await self.request.json()
        new_ads = Ads(**json_data)
        try:
            self.session.add(new_ads)
            await self.session.commit()
        except IntegrityError as err:
            raise get_http_error(web.HTTPConflict, "advertisement already exists")
        return web.json_response({"id": new_ads.id})

    async def patch(self):
        json_data = await self.request.json()
        ads = await ads_get(self.ads_id, self.session)
        for key, value in json_data.items():
            setattr(ads, key, value)
        try:
            self.session.add(ads)
            await self.session.commit()
        except IntegrityError as err:
            raise get_http_error(web.HTTPConflict, "advertisement already exists")
        return web.json_response({"status": "success"})

    async def delete(self):
        ads = await ads_get(self.ads_id, self.session)
        await self.session.delete(ads)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


app.add_routes(
    [
        web.get("/ads/{ads_id:\d+}/", AdsView),
        web.patch("/ads/{ads_id:\d+}/", AdsView),
        web.delete("/ads/{ads_id:\d+}/", AdsView),
        web.post("/ads/", AdsView),
    ]
)


if __name__ == "__main__":
    web.run_app(app)
