#!/usr/bin/env python3

from numpy import datetime64
import requests
import json
import datetime
import pytest
from .natusfera import (
    get_project_from_id,
    get_obs_from_query,
    get_obs_from_id,
    get_obs_from_user,  
    get_obs_from_project,
    get_project_from_name,
    get_obs_from_taxon,
    get_ids_from_place,
    get_obs_from_place_id,
    get_obs_from_place_name
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

    result = get_project_from_id(806)

    assert result['id'] == 806
    assert result['taxon'] == 'Fungi'

    # assert result['id'] == 806


def test_get_obs_from_query_returns_observations_data_when_less_than_pagination(requests_mock):
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page=1',
        json=[{
            "id": id, 
            "taxon_id": 3, 
            "created_at": "2021-03-15"} for id in range(100)],
    )
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page=100',
        json=[],
    )

    result = get_obs_from_query("quercus quercus")

    assert len(result) == 100
    assert result[0]["id"] == 0
    assert result[0]["taxon_id"] == 3
    assert type(result[0]["created_at"]) == datetime.datetime
    
def test_get_observations_returns_observations_data_when_more_than_pagination(
    requests_mock,
    ) -> None:
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page=1',
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

    result = get_obs_from_query("quercus quercus")

    assert len(result) == 250
    assert result[0]["id"] == 0
    assert result[0]["taxon_id"] == 3


def test_get_observations_returns_error_when_more_than_20000_results(
    requests_mock,
    ) -> None:
    """The API will return an error."""
    for page in range(1, 101):
        requests_mock.get(
            f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page={page}',
            json=[
                {"id": id_, "taxon_id": 3}
                for id_ in range(200 * (page - 1), 200 * page + 1)
            ],
        )
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page=101',
        json={"message": "You reach 20,000 items limit"},
    )

    with pytest.raises(
        ValueError,
        match="Number of results out of range. Need to add more filters"
    ):
        get_obs_from_query("quercus quercus")


def test_get_observations_by_id_returns_observations_data(
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

    result = get_obs_from_id(2084)

    assert result["id"] == 2084
    assert result["taxon_id"] == 3
    assert result['created_at'] == datetime.datetime(2016, 5, 1, 6, 32, 3, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=50400)))
    assert result['observed_on'] == datetime.datetime(2016, 5, 1, 0, 0)
    assert result['updated_at'] == datetime.datetime(2021, 3, 15, 1, 19, 22, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=50400)))


def test_get_obs_from_user_returns_observations_data(
    requests_mock,
    ) -> None:
    requests_mock.get(
        f"{API_URL}/observations/zolople.json?per_page=200&page=1",
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
    
    result = get_obs_from_user("zolople")
    #__import__("pdb").set_trace()

    assert len(result) == 260
    assert result[0]["user_login"] == "zolople"
    assert result[0]["id"] == 2084
    assert result[0]["taxon_id"] == 3


def test_get_obs_project_returns_observations_data(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/observations/project/806.json?per_page=200&page=1",
        json=[
            {"user_login": "zolople", 
            "id": 2084, 
            "taxon_id": 3} for id_ in range(37)],
    )
    result = get_obs_from_project(806)
    
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

    result = get_project_from_name('urbamar')

    assert result['id'] == 1191
    assert len(result) == 6
    assert type(result['updated_at']) == datetime.datetime

def test_get_obs_from_taxon_returns_info_with_pagination(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/observations.json?iconic_taxa=Fungi&per_page=200&page=1",
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
    result = get_obs_from_taxon('Fungi')

    assert len(result) == 456
    assert type(result[0]['updated_at']) == datetime.datetime


def test_get_ids_from_place_returns_list_ids(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/places.json?q=Barcelona",
        json=[{'display_name': 'Barcelona, Catalonia, ES',
                'id': 20, 
                'name': 'Barcelona'},
            {'display_name': 'Barcelona, Catalonia, ES',
                'id': 66,
                'name': 'Barcelona'},
            {'display_name': 'Barcelona, Catalonia, ES',
                'id': 67,
                'name': 'Barcelona'},
            {'display_name': 'Barcelona, Catalonia, ES',
            'id': 1011,
            'name': 'Barcelona'},
            {'display_name': 'Barcelona, Catalonia, ES',
            'id': 424,
            'name': 'Barcelona'},
            {'display_name': 'Barcelona, Catalonia, ES',
            'id': 425,
            'name': 'Barcelona'}]
            )
    result = get_ids_from_place("Barcelona")
    
    assert len(result) == 6
    assert type(result) == list
    assert 424 in result

def test_get_obs_from_place_id_returns_obs(requests_mock,) -> None:
    requests_mock.get(
        f"{API_URL}/observations.json?place_id=1011&per_page=200&page=1",
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
    result = get_obs_from_place_id(1011)
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
    

    result = get_obs_from_place_name("Barcelona")
    
    assert len(result) > 200

    place_ids = []
    for observation in result:
        place_ids.append(observation['place_id'])
    assert len(place_ids) > 1

    assert type(result[0]['updated_at']) == datetime.datetime