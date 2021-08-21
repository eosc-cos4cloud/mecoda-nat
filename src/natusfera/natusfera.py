#!/usr/bin/env python3
from typing import List, Dict, Any, Union, Optional
import requests
import datetime
from .models import Observation, Project, Taxon, Photo
from contextlib import suppress

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

def _get_ids_from_place(place:str) -> list:
    place_ids = []
    url = f"{API_URL}/places.json?q={place}"
    page = requests.get(url, verify=False)

    for dct in page.json():
        place_id = dct['id']
        place_ids.append(place_id)
    return place_ids

def get_project(p: Union[str, int]) -> List[Project]:
    """Download information of a project from id or name"""  

    if type(p) is int:
        url = f"{API_URL}/projects/{p}.json"
        page = requests.get(url, verify=False)
        
        if page.status_code == 404:
            print("ID No encontrado")
            exit
        else:
            resultado = [Project(**page.json())]
            return resultado

    elif type(p) is str:
        url = f"{API_URL}/projects/search.json?q={p}"
        page = requests.get(url, verify=False)
        resultado = [Project(**proj) for proj in page.json()]
        return resultado


def _build_url(
    query: Optional[str] = None, 
    id_project: Optional[int] = None,
    id_obs: Optional[int] = None,
    user: Optional[str] = None,
    taxon: Optional[str] = None,
    place_id: Optional[int] = None,
    year: Optional[int] = None,
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
    if year is not None:
        args.append(f"year={year}")

    url = f'{base_url}?{"&".join(args)}&per_page=200'
    #sin parametros devuelve los últimos registros

    return url

def _build_observations(observations_data: List[Dict[str, Any]]) -> Observation:
    observations = []
    
    for data in observations_data:
        
        with suppress(KeyError):
            data["taxon"] = Taxon(
                id=data['taxon']['id'],
                name=data['taxon']['name'],
                iconic_taxon=data['iconic_taxon_id'],
            )
        
        with suppress(KeyError):
            data["project_ids"] = [proj['project_id'] for proj in data['project_observations']]
    
        with suppress(KeyError):
            data['photos'] = []
            for observation_photo in data['observation_photos']:
                data['photos'].append(Photo(
                    id=observation_photo['id'],
                    large_url=observation_photo['photo']['large_url'],
                    medium_url=observation_photo['photo']['medium_url'],
                    small_url=observation_photo['photo']['small_url'],
                ))

        with suppress(KeyError):
            data['iconic_taxon'] = data['iconic_taxon_id']
        

        observation = Observation(**data)

        observations.append(observation)
    
    return observations

def _request(arg_url: str) -> List[Observation]:
    observations = []
    n = 1
    page = requests.get(arg_url)

    while len(page.json()) == 200:
        n += 1
        if n > 100:
            print("WARNING: Only the first 20,000 results are displayed")
            break
        observations.extend(_build_observations(page.json()))
        url = f"{arg_url}&page={n}"
        page = requests.get(url)
    
    if type(page.json()) is list:
        observations.extend(_build_observations(page.json()))
    else:
        observations.extend(_build_observations([page.json()]))
    
    return observations

def get_obs(
    query: Optional[str] = None, 
    id_project: Optional[int] = None,
    id_obs: Optional[int] = None,
    user: Optional[str] = None,
    taxon: Optional[str] = None,
    place_id: Optional[int] = None,
    place_name: Optional[str] = None,
    year: Optional[int] = None,
    ) -> List[Observation]:

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
                year,
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
            year,
            )

        observations = _request(url)

    return observations

def get_count_by_taxon() -> Dict:
    url = "https://natusfera.gbif.es/taxa.json"
    page = requests.get(url, verify=False)
    taxa = page.json()
    count = {}
    for taxon in taxa:
        count[taxon['name']] = taxon['observations_count']
    return count