#!/usr/bin/env python3

from numpy import datetime64
import requests
import json
import datetime
import pytest
from .natusfera import (
    get_project,
    get_obs
)

API_URL = "https://natusfera.gbif.es"


def test_get_project_from_id_extract_observation_data(requests_mock):
    requests_mock.get(
        f'{API_URL}/projects/806.json',
        json = {
            'title': 'titulo',
            'id': 806,
            'taxon': 'Fungi',
        }
    )
    result = get_project(806)

    assert result['id'] == 806
    assert result['taxon'] == 'Fungi'


def test_get_obs_from_query_returns_observations_data_when_less_than_pagination(requests_mock):
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200',
        json=[{
            "id": id, 
            "taxon_id": 3, 
            "created_at": "2021-03-15"} for id in range(100)],
    )
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page=100',
        json=[],
    )

    result = get_obs(query="quercus quercus")

    assert len(result) == 100
    assert result[0]["id"] == 0
    assert result[0]["taxon_id"] == 3
    assert type(result[0]["created_at"]) == datetime.datetime
    
def test_get_obs_returns_observations_data_when_more_than_pagination(
    requests_mock,
    ) -> None:
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200',
        json=[{"id": id_, "taxon_id": 3} for id_ in range(200)],
    )
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page=2',
        json=[{"id": id_, "taxon_id": 3} for id_ in range(200, 250)],
    )
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page=100',
        json=[],
    )

    result = get_obs(query="quercus quercus")

    assert len(result) == 250
    assert result[0]["id"] == 0
    assert result[0]["taxon_id"] == 3


def test_get_obs_returns_error_when_more_than_20000_results(
    requests_mock,
    capsys,
    ) -> None:
    """The API will return an error."""
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200',
        json=[
            {"id": id_, "taxon_id": 3}
            for id_ in range(0, 200)
        ],
    )
    for page in range(2, 100):
        requests_mock.get(
            f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page={page}',
            json=[
                {"id": id_, "taxon_id": 3}
                for id_ in range(200 * (page - 1), 200 * page)
            ],
        )
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page=101',
        json={"message": "You reach 20,000 items limit"},
    )

    result = get_obs("quercus quercus")

    # captura el mensaje de error que aparece en el output
    out, err = capsys.readouterr()
    
    assert len(result) == 20000
    assert "WARNING: Only the first 20,000 results are displayed" in out
    
    


def test_get_obs_by_id_returns_observations_data(
    requests_mock,
    ) -> None:
    requests_mock.get(
        f"{API_URL}/observations/2084.json",
        json={
            "id": 2084, 
            "taxon_id": 3, 
            'created_at': '2016-05-01T06:32:03-10:00',
            'observed_on': '2016-05-01',
            'updated_at': '2021-03-15T01:19:22-10:00',
        },
    )

    result = get_obs(id_obs=2084)
    assert len(result) == 1
    assert result[0]["id"] == 2084
    assert result[0]["taxon_id"] == 3
    assert result[0]['created_at'] == datetime.datetime(2016, 5, 1, 6, 32, 3, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=50400)))
    assert result[0]['observed_on'] == datetime.datetime(2016, 5, 1, 0, 0)
    assert result[0]['updated_at'] == datetime.datetime(2021, 3, 15, 1, 19, 22, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=50400)))


def test_get_obs_from_user_returns_observations_data(
    requests_mock,
    ) -> None:
    requests_mock.get(
        f"{API_URL}/observations/zolople.json?per_page=200",
        json=[
            {"user_login": "zolople", 
            "id": 2084, 
            "taxon_id": 3} for id_ in range(200)],
    )
    requests_mock.get(
        f"{API_URL}/observations/zolople.json?per_page=200&page=2",
        json=[{
            "user_login": "zolople", 
            "id": 2084, 
            "taxon_id": 3} for id_ in range(200, 260)],
    )
    
    result = get_obs(user="zolople")
    #__import__("pdb").set_trace()

    assert len(result) == 260
    assert result[0]["user_login"] == "zolople"
    assert result[0]["id"] == 2084
    assert result[0]["taxon_id"] == 3


def test_get_obs_project_returns_observations_data(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/observations/project/806.json?per_page=200",
        json=[
            {"user_login": "zolople", 
            "id": 2084, 
            "taxon_id": 3} for id_ in range(37)],
    )
    result = get_obs(id_project=806)
    
    assert len(result) == 37

def test_get_project_from_name_returns_observations_data(requests_mock,) -> None:
    requests_mock.get(
        "https://natusfera.gbif.es/projects/search.json?q=urbamar",
        json={
            'id': 1191,
            'latitude': '41.403373',
            'longitude': '2.216873',
            'updated_at': '2020-09-26',
            'place_id': None,
            'title': 'URBAMAR',
        }
    )

    result = get_project('urbamar')

    assert result['id'] == 1191
    assert len(result) == 6
    assert type(result['updated_at']) == datetime.datetime

def test_get_obs_from_taxon_returns_info_with_pagination(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/observations.json?iconic_taxa=Fungi&per_page=200",
        json=[{
            "taxon": "Fungi", 
            "id": 1645, 
            "taxon_id": 3,
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(200)
            ]
    )
    requests_mock.get(
        f"{API_URL}/observations.json?iconic_taxa=Fungi&per_page=200&page=2",
        json=[{
            "taxon": "Fungi", 
            "id": 1645, 
            "taxon_id": 3,
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(200)
        ]
    )
    requests_mock.get(
        f"{API_URL}/observations.json?iconic_taxa=Fungi&per_page=200&page=3",
        json=[{
            "taxon": "Fungi", 
            "id": 1645, 
            "taxon_id": 3,
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(56)
        ]
    )
    result = get_obs(taxon='Fungi')

    assert len(result) == 456
    assert type(result[0]['updated_at']) == datetime.datetime


def test_get_obs_from_place_id_returns_obs(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/observations.json?place_id=1011&per_page=200",
        json=[{
            "taxon": "Fungi", 
            "id": 1645, 
            "taxon_id": 3,
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(200)
            ]
    )
    requests_mock.get(
        f"{API_URL}/observations.json?place_id=1011&per_page=200&page=2",
        json=[{
            "taxon": "Fungi", 
            "id": 1645, 
            "taxon_id": 3,
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(200)
        ]
    )
    requests_mock.get(
        f"{API_URL}/observations.json?place_id=1011&per_page=200&page=3",
        json=[{
            "taxon": "Fungi", 
            "id": 1645, 
            "taxon_id": 3,
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(56)
        ]
    )
    result = get_obs(place_id=1011)
    assert len(result) == 456
    assert type(result[0]['updated_at']) == datetime.datetime

def test_get_obs_from_place_name_returns_obs(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/places.json?q=Barcelona",
        json=[{'id': 20}, {'id': 67}, {'id': 1024}]
        )
    requests_mock.get(
        f"{API_URL}/observations.json?place_id=20&per_page=200&page=1",
        json=[{
            "id": id_, 
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(200)]
        )
    requests_mock.get(
        f"{API_URL}/observations.json?place_id=20&per_page=200&page=2",
        json=[{
            "id": id_, 
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(56)]
        )
    requests_mock.get(
        f"{API_URL}/observations.json?place_id=67&per_page=200&page=1",
        json=[]
        )
    requests_mock.get(
        f"{API_URL}/observations.json?place_id=1024&per_page=200&page=1",
        json=[{
            "id": id_, 
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(5)]
        )
    

    result = get_obs(place_name="Barcelona")
    
    assert len(result) > 200

    place_ids = []
    for observation in result:
        place_ids.append(observation['place_id'])
    assert len(place_ids) > 1

    assert type(result[0]['updated_at']) == datetime.datetime

# test para nombre de place_name que no devuelve nada
def test_get_obs_from_place_name_returns_obs(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/places.json?q=Cuntis",
        json=[]
        )
    
    result = get_obs(place_name="Cuntis")
    
    assert len(result) == 0

# test de uso de la función con taxon en minúsculas
def test_get_obs_from_taxon_min_returns_info(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/observations.json?iconic_taxa=Fungi&per_page=200",
        json=[{
            "taxon": "Fungi", 
            "id": 1645, 
            "taxon_id": 3,
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(200)
            ]
    )
    requests_mock.get(
        f"{API_URL}/observations.json?iconic_taxa=Fungi&per_page=200&page=2",
        json=[{
            "taxon": "Fungi", 
            "id": 1645, 
            "taxon_id": 3,
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(200)
        ]
    )
    requests_mock.get(
        f"{API_URL}/observations.json?iconic_taxa=Fungi&per_page=200&page=3",
        json=[{
            "taxon": "Fungi", 
            "id": 1645, 
            "taxon_id": 3,
            'updated_at': '2020-09-26T05:07:36-10:00',} for id_ in range(56)
        ]
    )
    result = get_obs(taxon='fungi')

    assert len(result) == 456
    assert type(result[0]['updated_at']) == datetime.datetime

# test de usos combinados
def test_get_obs_from_combined_arguments(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/observations/zolople.json?iconic_taxa=Mollusca&per_page=200",
        json=[{
            "taxon": "Mollusca",
            "id": id_,
            "taxon_id": 3,
            "user": "zolople",
            "created_at": '2020-09-26',} for id_ in range(5)
            ]
    )
    result = get_obs(taxon="Mollusca", user="zolople")

    assert len(result) == 5
    assert result[0]['created_at'] == datetime.datetime(2020, 9, 26)

# test combinado id_project, place_id, query
def test_get_obs_from_three_combined_arguments(requests_mock,) -> None:
    requests_mock.get(
        f'{API_URL}/observations/project/45.json?place_id=3&q="quercus quercus"&per_page=200',
        json=[
            {"id": 4586, "project": 45, "place": 3, "species": "quercus quercus"},
            {"id": 4588, "project": 45, "place": 3, "species": "quercus quercus"},
        ]
    )
    result = get_obs(id_project=45, place_id=3, query="quercus quercus")

    assert len(result) == 2

