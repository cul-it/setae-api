from typing import Callable, Optional
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute
from json2xml import json2xml
from json2xml.utils import readfromstring
from lxml import etree
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
async def read_item(
    barcode: int, format: Optional[str] = "xml", transform: Optional[bool] = True
):
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
        # FOLIO /inventory/items endpoint always returns list
        # -- trim to single item because SpineOMatic expects object as root node
        item = data["items"][0]
        xml_raw = json2xml.Json2xml(item, wrapper="item").to_xml()

        if transform:
            # Transform XML to align with ALMA's RESTful API response
            transform = etree.XSLT(etree.parse("./alma-rest-item.xsl"))
            result = transform(etree.fromstring(xml_raw))
            xml = bytes(result)

        else:
            xml = xml_raw

        return Response(content=xml, media_type="application/xml")


app.include_router(router)
