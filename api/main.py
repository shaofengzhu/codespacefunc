from __future__ import annotations

import azure.functions as func
import json
import logging
import sys
from urllib.parse import unquote

from pathlib import Path
sys.path.insert(0, str(Path(__file__).absolute().parent))
from handlers import execute_function, get_all_metadata
del sys.path[0]


def main(req: func.HttpRequest) -> func.HttpResponse:
    # Defer the import until triggered so that failure is attached to the response
    try:
        import Functions
    except ModuleNotFoundError:
        # Try the Azure Functions name if the "natural" name was missing
        import __app__.Functions as Functions

    invokeFunction = False
    if req.method == "POST":
        try:
            invokeFunction = True
            payload = req.get_json()
        except Exception as ex:
            return func.HttpResponse(f"Invalid request: {ex}", status_code=400)

    _, _, param = req.url.partition("?")
    if req.method == "GET" and param.startswith("invoke="):
        invokeFunction = True
        payload = param.partition("=")[2]
        payload = json.loads(unquote(payload))

    if invokeFunction:
        try:
            return func.HttpResponse(
                execute_function(Functions, payload),
                mimetype="application/json",
            )
        except Exception as ex:
            return func.HttpResponse(f"Invalid request: {ex}", status_code=422)


    return func.HttpResponse(get_all_metadata(Functions), mimetype="application/json")
