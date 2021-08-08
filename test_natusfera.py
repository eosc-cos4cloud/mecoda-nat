#!/usr/bin/env python3

import requests
import json
import datetime
from .natusfera import (
    get_project_from_id,
    get_obs_from_query,
    get_obs_from_id,
    get_obs_from_user,  
    get_obs_project,
)

API_URL = "https://natusfera.gbif.es"


def test_get_get_project_from_id_extract_observation_data(requests_mock):

    json_resultado = '''
    {
        "description": "Observaci\u00f3n de la biodiversidad que se encuentra en el ecosistema del r\u00edo Arga",
        "id": 806,
        "title": "Proyecto r\u00edo Arga-Arga ibaiko proiektua",
    }
    '''
    requests_mock.get("https://natusfera.gbif.es/projects/806.json", text=json_resultado)

    result = get_project_from_id(806)

    assert result == json.loads(json_resultado)

    # assert result['id'] == 806


def test_get_obs_from_query_returns_observations_data_when_less_than_pagination(requests_mock):
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page=1',
        json=[{"id": id, "taxon_id": 3} for id in range(100)],
    )
    requests_mock.get(
        f'{API_URL}/observations.json?q="quercus quercus"&per_page=200&page=100',
        json=[],
    )

    result = get_obs_from_query("quercus quercus")

    assert len(result) == 100
    assert result[0]["id"] == 0
    assert result[0]["taxon_id"] == 3


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


import pytest

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

def test_get_obs_project_returns_observations_data(requests_mock,
) -> None:
    requests_mock.get(
        f"{API_URL}/observations/project/806.json?per_page=200&page=1",
        json=[
            {"user_login": "zolople", 
            "id": 2084, 
            "taxon_id": 3} for id_ in range(37)],
    )
    result = get_obs_project(806)
    
    assert len(result) == 37
