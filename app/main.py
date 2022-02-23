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


@app.get("/solr/{hrid}")
async def solr_item(hrid: int):
    url = f"{os.getenv('SOLR_URL')}/get"
    params = {"ids": hrid}

    solr_items = requests.get(url, params=params)
    data = readfromstring(solr_items.text)
    doc = data["response"]["docs"][0]
    holdings = readfromstring(doc["holdings_json"])
    items = readfromstring(doc["items_json"])

    rebuilt = [{k: v} for k, v in holdings.items()]

    for h in rebuilt:
        first_key = next(iter(h))
        h[first_key]["availableCount"] = 0
        h[first_key]["totalCount"] = 0
        h[first_key]["nextDue"] = []
        h[first_key]["items"] = []

    for item_vals in items.values():
        for item in item_vals:
            status = item["status"].get("status")
            due = item["status"].get("due")
            for holding in rebuilt:
                for holding_val in holding.values():
                    if item["call"] == holding_val["call"]:
                        holding_val["totalCount"] += 1
                        if status == "Available":
                            holding_val["availableCount"] += 1
                        holding_val["items"].append(item)
                        # TODO: Test due date is in the future!
                        # -- FOLIO does not automatically update status once due date
                        # -- has past and item remains "Checked out". Additionally,
                        # -- FOLIO has no "Overdue" or "Late" status. Yay!
                        if due and status == "Checked out":
                            holding_val["nextDue"].append(due)

    for holding in rebuilt:
        for holding_val in holding.values():
            if holding_val["nextDue"]:
                holding_val["nextDue"] = sorted(holding_val["nextDue"])[0]
            else:
                holding_val["nextDue"] = None
    return rebuilt


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

    if format == "json":
        return folio_inventory.json()
    else:
        data = readfromstring(folio_inventory.text)
        # FOLIO /inventory/items endpoint always returns list
        # -- trim to single item because SpineOMatic expects object as root node
        try:
            item = data["items"][0]

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
    url = f"{os.getenv('OKAPI_URL')}/authn/login"
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
