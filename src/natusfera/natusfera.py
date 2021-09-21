#!/usr/bin/env python3
from .models import Project, Observation, TAXONS, ICONIC_TAXON, Taxon, Photo
from typing import List, Dict, Any, Union, Optional
import requests
from contextlib import suppress
#from pydantic import ValidationError
import urllib3
import pandas as pd
import flat_table
import os
import shutil

urllib3.disable_warnings()

# Definición de variables
API_URL = "https://natusfera.gbif.es"

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
    project_name: Optional[str] = None,
    id_obs: Optional[int] = None,
    user: Optional[str] = None,
    taxon: Optional[str] = None,
    place_id: Optional[int] = None,
    year: Optional[int] = None,
    ) -> str:
    
    if project_name is not None:
        id_project = get_project(project_name)[0].id
    
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
            if data['place_guess'] is not None:
                data['place_name'] = data['place_guess'].replace("\r\n", ' ').strip()

        try:
            data["taxon"] = Taxon(
                id=data['taxon']['id'],
                name=data['taxon']['name'],
                ancestry=data['taxon']['ancestry']
            )
        except KeyError:
            data['taxon'] = None
    
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

        with suppress(KeyError):
            data['iconic_taxon'] = ICONIC_TAXON[data['iconic_taxon_id']]
        
        # eliminación de saltos de línea en el campo description
        with suppress(KeyError):
            if data['description'] is not None:
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
    project_name: Optional[str] = None,
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
                project_name,
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
            project_name,
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


# Función para extraer dataframe de observaciones y dataframe de photos
def get_dfs(observations) -> pd.DataFrame:
    
    df = pd.DataFrame([obs.dict() for obs in observations])
    df2 = df.drop(['photos'], axis=1)

    df_observations = flat_table.normalize(df2).drop(['index'], axis=1)
    df_observations['created_at'] = df_observations['created_at'].apply(lambda x: x.date())
    df_observations['updated_at'] = df_observations['updated_at'].apply(lambda x: x.date())
    df_observations['taxon.id'] = df_observations['taxon.id'].astype('Int64', errors='ignore')
    df_observations['longitude'] = df_observations['longitude'].astype('float', errors='ignore')
    df_observations['latitude'] = df_observations['latitude'].astype('float', errors='ignore')

    df_photos = flat_table.normalize(df[['id', 'photos', 'iconic_taxon', 'taxon', 'user_login', 'latitude', 'longitude']]).drop(['index'], axis=1)
    df_photos = df_photos[['id', 'photos.id', 'iconic_taxon', 'taxon.name', 'photos.medium_url', 'user_login', 'latitude', 'longitude']]
    
    df_photos['longitude'] = df_photos['longitude'].astype('float', errors='ignore')
    df_photos['latitude'] = df_photos['latitude'].astype('float', errors='ignore')

    df_photos['path'] = df_photos['id'].astype(str) + "_" + df_photos['photos.id'].astype(str) + ".jpg"
    df_observations['photo.id'] = df_observations['photo.id'].astype('Int64', errors='ignore')
    
    return df_observations, df_photos

# Función para descargar las fotos resultado de la consulta
def download_photos(df_photos: pd.DataFrame, directorio: Optional[str] = "./natusfera_photos"):
    
    # Crea la carpeta, si existe la sobreescribre
    if os.path.exists(directorio):
        shutil.rmtree(directorio)
    os.makedirs(directorio)

    # Itera por el df_photos resultado de la consulta y descarga las fotos en tamaño medio
    for n in range(len(df_photos)):
        row = df_photos.iloc[[n]]
        response = requests.get(row['photos.medium_url'][n], verify=False, stream=True)
        if response.status_code == 200:
            with open(f"{directorio}/{row['path'][n]}", 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
        del response
    df_photos['path'] = df_photos['path'].apply(lambda x: os.path.abspath(f"{directorio}/{x}"))