from typing import Optional
from fastapi import FastAPI, Response
from json2xml import json2xml
from json2xml.utils import readfromstring
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{barcode}")
async def read_item(barcode: int, format: Optional[str] = "xml"):
    url = "https://okapi-cornell-test.folio.ebsco.com/inventory/items"
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

