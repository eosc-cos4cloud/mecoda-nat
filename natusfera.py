#!/usr/bin/env python3
from typing import List, Union, Optional
import requests
from bs4 import BeautifulSoup
import datetime
from typing import Dict, List

API_URL = "https://natusfera.gbif.es"

TAXONS = [
    "Chromista",
    "Protozoa",
    "Animalia",
    "Mollusca",
    "Arachnida",
    "Insecta",
    "Aves",
    "Mammalia",
    "Amphibia",
    "Reptilia",
    "Actinopterygii",
    "Fungi",
    "Plantae",
    "Unknown"
]

def _convert_to_datetime(observations: list) -> list:
    campos = ["created_at", "observed_on", "updated_at"]

    for observation in observations:
        for campo in campos:
            try:
                if type(observation[campo]) != datetime.datetime:
                    observation[campo] = datetime.datetime.fromisoformat(observation[campo])
            except KeyError:
                pass
    return observations

def _get_ids_from_place(place:str) -> list:
    place_ids = []
    url = f"{API_URL}/places.json?q={place}"
    page = requests.get(url, verify=False)

    for dct in page.json():
        place_id = dct['id']
        place_ids.append(place_id)
    return place_ids

def get_project(p: Union[str, int]) -> Dict:
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

def _build_url(
    query: Optional[str] = None, 
    id_project: Optional[int] = None,
    id_obs: Optional[int] = None,
    user: Optional[str] = None,
    taxon: Optional[str] = None,
    place_id: Optional[int] = None,
    ) -> str:

    # definir la base url
    if id_project is not None:
        base_url = f"{API_URL}/observations/project/{id_project}.json"
    elif id_obs is not None:
        base_url = f"{API_URL}/observations/{id_obs}.json"
    elif user is not None:
        base_url = f"{API_URL}/observations/{user}.json"
    else:
        base_url = f"{API_URL}/observations.json"
    
    # definir los argumentos que admite la API
    args = []
    if query is not None:
        args.append(f'q="{query}"')
    if taxon is not None:
        taxon = taxon.title()
        if taxon in TAXONS:
            args.append(f"iconic_taxa={taxon}")
        else:
            raise ValueError("No es una taxonomía válida")
    if place_id is not None:
        args.append(f"place_id={place_id}")

    
    url = f'{base_url}?{"&".join(args)}&per_page=200'

    return url

def _request(arg_url: str) -> List:
    observations = []
    n = 1
    page = requests.get(arg_url)
    #__import__("pdb").set_trace()

    while len(page.json()) == 200:
        
        n += 1
        if n > 100:
            print("WARNING: Only the first 20,000 results are displayed")
            break
        observations.extend(page.json())
        url = f"{arg_url}&page={n}"
        page = requests.get(url)
    
    if type(page.json()) == list:
        observations.extend(page.json())
    else:
        observations.append(page.json())
    
    return observations

def get_obs(
    query: Optional[str] = None, 
    id_project: Optional[int] = None,
    id_obs: Optional[int] = None,
    user: Optional[str] = None,
    taxon: Optional[str] = None,
    place_id: Optional[int] = None,
    place_name: Optional[str] = None,
    ) -> List:

    if place_name is not None:
        place_ids = _get_ids_from_place(place_name)
        observations = []
        for place_id in place_ids:
            url = _build_url(
                query, 
                id_project,
                id_obs,
                user,
                taxon,
                place_id,
                )
            observations.extend(_request(url))
    else:
        url = _build_url(
            query, 
            id_project,
            id_obs,
            user,
            taxon,
            place_id,
            )

        observations = _request(url)

    return _convert_to_datetime(observations)

