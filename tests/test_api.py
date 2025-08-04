import json
import os
import pytest
from unittest.mock import patch, Mock

import requests
# import rdflib

from locpy.api import LocAPI, SRUItem


FIXTURES_PATH = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestLocAPI(object):
    def test_get_uri(self):
        assert (
            LocAPI.uri_from_id('n79043402') == 'http://id.loc.gov/authorities/n79043402'
        )

    def test_get_rwo_uri(self):
        assert (
            LocAPI.rwo_uri_from_id('n79043402')
            == 'http://id.loc.gov/rwo/agents/n79043402'
        )

    def test_get_lcnaf_uri(self):
        assert (
            LocAPI.dataset_uri_from_id('n79043402')
            == 'http://id.loc.gov/authorities/names/n79043402'
        )

    def test_get_lcsh_uri(self):
        assert (
            LocAPI.dataset_uri_from_id('sh85100849')
            == 'http://id.loc.gov/authorities/subjects/sh85100849'
        )

    def test_get_lcsj_uri(self):
        assert (
            LocAPI.dataset_uri_from_id('sj2021051581')
            == 'http://id.loc.gov/authorities/childrensSubjects/sj2021051581'
        )

    def test_get_lcmpt_uri(self):
        assert (
            LocAPI.dataset_uri_from_id('mp2013015252')
            == 'http://id.loc.gov/authorities/performanceMediums/mp2013015252'
        )

    def test_get_dgt_uri(self):
        assert (
            LocAPI.dataset_uri_from_id('dg2015060711')
            == 'http://id.loc.gov/authorities/demographicTerms/dg2015060711'
        )

    def test_get_tgm_uri(self):
        assert (
            LocAPI.dataset_uri_from_id('tgm000641')
            == 'http://id.loc.gov/vocabulary/graphicMaterials/tgm000641'
        )

    def test_get_afset_uri(self):
        assert (
            LocAPI.dataset_uri_from_id('afset000851')
            == 'http://id.loc.gov/vocabulary/ethnographicTerms/afset000851'
        )

    def test_get_lcgft_uri(self):
        assert (
            LocAPI.dataset_uri_from_id('gf2023026091')
            == 'http://id.loc.gov/authorities/genreForms/gf2023026091'
        )

    def test_not_lcsh_err(self):
        with pytest.raises(ValueError):
            LocAPI.dataset_uri_from_id('TR658.3')

    @patch('locpy.api.requests')
    def test_retrieve_label(self, mockrequests):
        loc = LocAPI()
        # abbreviated successful request
        mock_headers = {
            'location': 'https://id.loc.gov/authorities/names/n79043402',
            'x-uri': 'http://id.loc.gov/authorities/names/n79043402',
            'x-preflabel': 'Franklin, Benjamin, 1706-1790'
        }

        mock_response = Mock()
        mock_response.status_code = 302
        mock_response.headers = mock_headers
        mockrequests.get.return_value = mock_response

        assert loc.retrieve_label('Franklin, Benjamin, 1706-1790') == 'n79043402'

    # features to test for search results:
    # constructs URLs correctly for differing authorities
    # returns empty list with no results
    @patch('locpy.api.requests')
    def test_suggest(self, mockrequests):
        loc = LocAPI()
        mockrequests.codes = requests.codes
        # check that query with no results returns empty lists
        mock_result = {
            'q': 'notanentity',
            'count': 0,
            'pagesize': 10,
            'start': 1,
            'sortmethod': 'alpha',
            'searchtype': 'left-anchored',
            'directory': 'all',
            'hits': [],
        }
        mockrequests.get.return_value.status_code = requests.codes.ok
        mockrequests.get.return_value.json.return_value = mock_result
        assert loc.suggest('notanentity') == []
        mockrequests.get.assert_called_with(
            'http://id.loc.gov/suggest2', params={'q': 'notanentity'}
        )

        # test suggest results
        sru_fixture = os.path.join(FIXTURES_PATH, 'sru_search.json')
        with open(sru_fixture, encoding='utf-8') as srufile:
            mock_result = json.load(srufile)
        mockrequests.get.return_value.json.return_value = mock_result
        results = loc.suggest('Franklin, Benjamin')
        assert isinstance(results, list)
        assert isinstance(results[0], SRUItem)
        mockrequests.get.assert_called_with(
            'http://id.loc.gov/suggest2', params={'q': 'Franklin, Benjamin'}
        )

        # bad status code should return empty list
        mockrequests.get.return_value.status_code = requests.codes.forbidden
        assert loc.suggest('test') == []

    # not sure about these next two tests - what good do they serve?
    def test_suggest_names(self):
        loc = LocAPI()
        term = 'Franklin, Benjamin'
        with patch.object(loc, 'suggest') as mocksuggest:
            loc.suggest(term, authority='names')

        mocksuggest.assert_called_with('Franklin, Benjamin', authority='names')

    def test_suggest_subjects(self):
        loc = LocAPI()
        term = 'Franklin, Benjamin'
        with patch.object(loc, 'suggest') as mocksuggest:
            loc.suggest(term, authority='subjects')

        mocksuggest.assert_called_with('Franklin, Benjamin', authority='subjects')
