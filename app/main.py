from typing import Callable, Optional
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute
from json2xml import json2xml
from json2xml.utils import readfromstring
from dotenv import load_dotenv
import os
import requests

load_dotenv()


class StripSpineOMaticAPIKey(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # Srip apikey URL param hardcoded in SpineOMatic before passing to FOLIO
            # -- appended as '&apikey='
            clean_barcode = request.path_params["barcode"].partition("&")[0]
            request.path_params["barcode"] = clean_barcode
            response: Response = await original_route_handler(request)
            return response

        return custom_route_handler


app = FastAPI()
router = APIRouter(route_class=StripSpineOMaticAPIKey)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@router.get("/items/{barcode}")
async def read_item(barcode: int, format: Optional[str] = "xml"):
    url = f"{os.getenv('OKAPI_URL')}/inventory/items"
    params = {"query": f"(barcode=={barcode})"}
    headers = {
        "Content-Type": "application/json",
        "X-Okapi-Tenant": os.getenv("OKAPI_TENANT"),
        "X-Okapi-Token": os.getenv("OKAPI_TOKEN"),
    }
    folio_inventory = requests.get(url, params=params, headers=headers)

    if format == "json":
        return folio_inventory.json()
    else:
        data = readfromstring(folio_inventory.text)
        xml = json2xml.Json2xml(data).to_xml()
        return Response(content=xml, media_type="application/xml")


app.include_router(router)
