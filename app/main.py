from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute
from json2xml import json2xml
from json2xml.utils import readfromstring
from lxml import etree
from lxml.builder import E
from typing import Callable, List, Optional
import csv
import os
import re
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
    barcode: int,
    format: Optional[str] = "xml",
    replace: Optional[bool] = True,
    transform: Optional[bool] = True,
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
        try:
            item = data["items"][0]

            if replace:
                # String replacement for call number prefix & suffix
                # -- replacements managed via CSV in repo
                with open("./prefix-suffix.csv", newline="") as csvfile:
                    reader = csv.DictReader(csvfile)
                    replacements = [row for row in reader]

                prefix_regex = _reps_to_regex(replacements=replacements, field="prefix")
                suffix_regex = _reps_to_regex(replacements=replacements, field="suffix")

                callnumber_comps = item.get("effectiveCallNumberComponents", {})
                prefix = callnumber_comps.get("prefix")
                suffix = callnumber_comps.get("suffix")

                if prefix:
                    processed_prefix = _replace_string(
                        string=prefix, regex=prefix_regex
                    )
                    item["effectiveCallNumberComponents"]["prefix"] = processed_prefix

                if suffix:
                    processed_suffix = _replace_string(
                        string=suffix, regex=suffix_regex
                    )
                    item["effectiveCallNumberComponents"]["suffix"] = processed_suffix

            xml_raw = json2xml.Json2xml(item, wrapper="item").to_xml()

            if transform:
                # Transform XML to align with ALMA's RESTful API response
                transform = etree.XSLT(etree.parse("./alma-rest-item.xsl"))
                result = transform(etree.fromstring(xml_raw))
                xml = bytes(result)

            else:
                xml = xml_raw

        except IndexError:
            xml = etree.tostring(
                E.error(E.message(f"No item found for barcode {barcode}"))
            )

        return Response(content=xml, media_type="application/xml")


def _reps_to_regex(replacements: List, field: str):
    return [
        (fr"^{rep['string']}$", f"{rep['replacement']}")
        for rep in replacements
        if rep["field"] == field
    ]


def _replace_string(string: str, regex: List):
    for r in regex:
        string = re.sub(r[0], r[1], string, flags=re.IGNORECASE)
    return string


app.include_router(router)
