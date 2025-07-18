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
        "X-Okapi-Token": _okapi_login(),
    }
    folio_inventory = requests.get(url, params=params, headers=headers)
    plate_funds = ["p2053","p2052","p8655","p7351", "p6790", "p6692",
        "p4557","p3353","p3169","p3161","p3159",
        "p3157","p2980","p2966","p2964","p2962","p2960","p2959","p2860","p2858",
        "p2757","p2756","p2655","p2452","p2450","p2290","p2257","p2254","p2160"

]

    if format == "json":
        return folio_inventory.json()
    else:
        data = readfromstring(folio_inventory.text)
        # FOLIO /inventory/items endpoint always returns list
        # -- trim to single item because SpineOMatic expects object as root node
        try:
            item = data["items"][0]

            holdings = item["holdingsRecordId"]
            pol = requests.get(os.getenv('OKAPI_URL') + "/orders/holding-summary/" + holdings, headers=headers).json()
            if len(pol["holdingSummaries"]) > 0:
                pol = pol["holdingSummaries"][0]
                fund = requests.get(os.getenv('OKAPI_URL') + "/orders/order-lines/" + pol["poLineId"], headers=headers).json()
                if "fundDistribution" in fund:
                    for f in fund["fundDistribution"]:
                        if "code" in f and f["code"] in plate_funds:
                            print(f["code"])
                            item["fund"] = f["code"]
            
            


            # Trim spaces from call number components
            prefix, suffix = _trim_callno_components(item=item)

            if replace:
                # String replacement for call number prefix & suffix
                # -- replacements managed via CSV in repo
                with open("./prefix-suffix.csv", newline="") as csvfile:
                    reader = csv.DictReader(csvfile)
                    replacements = [row for row in reader]

                prefix_regex = _reps_to_regex(replacements=replacements, field="prefix")
                suffix_regex = _reps_to_regex(replacements=replacements, field="suffix")

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

        except IndexError:
            xml_raw = etree.tostring(
                E.error(E.message(f"No item found for barcode {barcode}"))
            )

        if transform:
            # Transform XML to align with ALMA's RESTful API response
            transform = etree.XSLT(etree.parse("./alma-rest-item.xsl"))
            result = transform(etree.fromstring(xml_raw))
            xml = bytes(result)

        else:
            xml = xml_raw

        return Response(content=xml, media_type="application/xml")


def _okapi_login():
    url = f"{os.getenv('OKAPI_URL')}/authn/login-with-expiry"
    headers = {
        "X-Okapi-Tenant": os.getenv("OKAPI_TENANT"),
    }
    data = {
        "username": os.getenv("OKAPI_USER"),
        "password": os.getenv("OKAPI_PASSWORD"),
    }
    r = requests.post(url, json=data, headers=headers)
    r.raise_for_status()
    if r.status_code == 201:
        cookies = r.headers.get("Set-Cookie")
        if cookies:
            for cookie in cookies.split(';'):
                if cookie.startswith("folioAccessToken="):
                    r.headers["X-Okapi-Token"] = cookie.split("=")[1].split(";")[0]
                    return r.headers["X-Okapi-Token"]
    return None

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


def _trim_callno_components(item: dict):
    """
    Collapse multiple spaces to singular and remove leading/tailing spaces.
    Returns call number prefix and suffix for later string replacement.
    """
    callno_comps = item.get("effectiveCallNumberComponents", {})

    comps = {
        "callNumber": callno_comps.get("callNumber"),
        "prefix": callno_comps.get("prefix"),
        "suffix": callno_comps.get("suffix"),
    }

    for k, v in comps.items():
        if comps[k]:
            item["effectiveCallNumberComponents"][k] = comps[k] = re.sub(
                " +", " ", v
            ).strip()

    return comps["prefix"], comps["suffix"]


app.include_router(router)
