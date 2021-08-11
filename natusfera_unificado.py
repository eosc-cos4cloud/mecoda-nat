#!/usr/bin/env python3
from typing import List
import requests
from bs4 import BeautifulSoup
import datetime

API_URL = "https://natusfera.gbif.es"

def get_project(p: str or int) -> dict:
    """Download information of a project from id or name"""  

    if type(p) is int:
        url = f"{API_URL}/projects/{p}.json"
    elif type(p) is str:
        url = f"{API_URL}/projects/search.json?q={p}"

    page = requests.get(url, verify=False)
    resultado = page.json()
    
    campos = ["created_at", "observed_on", "updated_at"]
    for campo in campos:
        try:
            if type(resultado[campo]) != datetime.datetime:
                resultado[campo] = datetime.datetime.fromisoformat(resultado[campo])
        except KeyError:
            pass

    return resultado