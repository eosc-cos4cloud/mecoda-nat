#!/usr/bin/env python3
from typing import List, Dict, Any, Union, Optional
import requests
from .models import Observation, Project, Taxon, Photo
from contextlib import suppress
import urllib3
urllib3.disable_warnings()

# Definición de variables
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

# Función para extraer los datos de un proyecto a partir de su nombre o id
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

# Función interna para extraer los posibles ids de un lugar a partir de una palabra
def _get_ids_from_place(place:str) -> list:
    place_ids = []
    url = f"{API_URL}/places.json?q={place}"
    page = requests.get(url, verify=False)

    for dct in page.json():
        place_id = dct['id']
        place_ids.append(place_id)
    return place_ids



# Función interna para construir la url a la que se hará la petición de observaciones
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
    
    #cuando no indicamos ningún parámetro, devuelve los últimos registros

    return url

# Función interna que toma una lista de diccionarios y devuelve una lista de objetos Observation
def _build_observations(observations_data: List[Dict[str, Any]]) -> List[Observation]:
    '''
    Construye objetos Observation a partir del JSON de observaciones de la API.

    Args:
        observations_data: lista de diccionarios. Cada uno contiene la información de una observación.
    
    '''
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
            lista_fotos = []
            for observation_photo in data['photos']:
                lista_fotos.append(Photo(
                    id=observation_photo['id'],
                    large_url=observation_photo['large_url'],
                    medium_url=observation_photo['medium_url'],
                    small_url=observation_photo['small_url'],
                ))
            data['photos'] = lista_fotos
            # devuelve siempre una lista vacía

        with suppress(KeyError):
            data['iconic_taxon'] = data['iconic_taxon_id']
        
        # eliminación de saltos de línea en el campo description
        with suppress(KeyError):
            data['description'] = data['description'].replace("\r\n", ' ')

        observation = Observation(**data)

        observations.append(observation)
    
    return observations

# Función interna que realiza la petición de la API y devuelve la lista de objetos Observation
def _request(arg_url: str, num_max: Optional[int] = None) -> List[Observation]:
    observations = []
    n = 1
    page = requests.get(arg_url, verify=False)

    if type(page.json()) is dict:
        observations.extend(_build_observations([page.json()]))
    
    else:
        while len(page.json()) == 200:
            observations.extend(_build_observations(page.json()))
            n += 1
            if n > 99:
                print("WARNING: Only the first 20,000 results are displayed")
                break
            if num_max is not None and len(observations) >= num_max:
                break
            url = f"{arg_url}&page={n}"
            page = requests.get(url, verify=False)
            print(f"Número de elementos: {len(observations)}")
            
        observations.extend(_build_observations(page.json()))
        
        if num_max:
            observations = observations[:num_max]

    print(f"Número de elementos: {len(observations)}")
    return observations

# Función para extraer las observaciones y que admite distintos filtros
def get_obs(
    query: Optional[str] = None, 
    id_project: Optional[int] = None,
    id_obs: Optional[int] = None,
    user: Optional[str] = None,
    taxon: Optional[str] = None,
    place_id: Optional[int] = None,
    place_name: Optional[str] = None,
    year: Optional[int] = None,
    num_max: Optional[int] = None,
    ) -> List[Observation]:

    print("Generando lista de observaciones:")

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
            observations.extend(_request(url, num_max))
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

        observations = _request(url, num_max)

    return observations

# Función que devuelve el número de observaciones registrado de cada familia taxonómica
def get_count_by_taxon() -> Dict:
    url = "https://natusfera.gbif.es/taxa.json"
    page = requests.get(url, verify=False)
    taxa = page.json()
    count = {}
    for taxon in taxa:
        count[taxon['name']] = taxon['observations_count']
    return count