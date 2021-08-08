#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import datetime

API_URL = "https://natusfera.gbif.es"

def get_project_from_id(id):
    url = f"{API_URL}/projects/{id}.json"
    page = requests.get(url)
    
    return page.json()

def get_obs_from_query(query):
    observations = []
    n = 1
    url = f'{API_URL}/observations.json?q="{query}"&per_page=200&page={n}'
    page = requests.get(url)
    if len(requests.get(f'{API_URL}/observations.json?q="{query}"&per_page=200&page=100').json()) < 200:
        while len(page.json()) == 200:
            observations.extend(page.json())
            n += 1
            url = f'{API_URL}/observations.json?q="{query}"&per_page=200&page={n}'
            page = requests.get(url)
        
        observations.extend(page.json())
    else:
        raise ValueError("Number of results out of range. Need to add more filters")
            
    #__import__("pdb").set_trace()
    return observations

def get_obs_from_id(id):
    """Get information on a specific observation given an id"""
    url = f'{API_URL}/observations/{id}.json'
    page = requests.get(url)
    
    return page.json()

def get_obs_from_user(user):
    """Download observations for a user"""
    observations = []
    n = 1
    url = f'{API_URL}/observations/{user}.json?per_page=200&page={n}'
    page = requests.get(url)
        
    while len(page.json()) == 200:
        observations.extend(page.json())
        n += 1
        url = f'{API_URL}/observations/{user}.json?per_page=200&page={n}'
        page = requests.get(url)
        
    observations.extend(page.json())
    
    #__import__("pdb").set_trace()

    return observations


def get_obs_project(id):
    """Download observations or info from a project"""
    observations = []
    n = 1
    url = f"https://natusfera.gbif.es/observations/project/{id}.json?per_page=200&page={n}"
    page = requests.get(url)

    while len(page.json()) == 200:
        observations.extend(page.json())
        n += 1
        url = f"https://natusfera.gbif.es/observations/project/{id}.json?per_page=200&page={n}"
        page = requests.get(url)
    
    observations.extend(page.json())

    return observations

taxon_name = [
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
    "unknown"
]

def get_project_from_name(name):
    """Download information of projects from name"""  
    
    url = f"https://natusfera.gbif.es/projects/search.json?q={name}"
    page = requests.get(url)
    
    return page.json()


#def get_obs_from_taxon(taxon)

#def get_obs_from_places(place)

#get_inat_obs(): Download iNaturalist data

#get_inat_obs_user(): Download observations for a user
#get_inat_obs_id(): Get information on a specific observation
#get_inat_obs_project(): Download observations or info from a project
