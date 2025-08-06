import json
import os
import pytest
from unittest.mock import patch, Mock

import requests
import rdflib

from locpy.api import LocAPI, SRUItem, LocEntity, NameEntity, SubjectEntity, SRUResult


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
            'x-preflabel': 'Franklin, Benjamin, 1706-1790',
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
        # this test also checks that authorities are passed correctly
        sru_fixture = os.path.join(FIXTURES_PATH, 'sru_suggest.json')
        with open(sru_fixture, encoding='utf-8') as srufile:
            mock_result = json.load(srufile)
        mockrequests.get.return_value.json.return_value = mock_result
        results = loc.suggest('Franklin, Benjamin', 'names')
        assert isinstance(results, list)
        assert isinstance(results[0], SRUItem)
        mockrequests.get.assert_called_with(
            'http://id.loc.gov/authorities/names/suggest2', params={'q': 'Franklin, Benjamin'}
        )

        # bad status code should return empty list
        mockrequests.get.return_value.status_code = requests.codes.forbidden
        assert loc.suggest('test') == []

    @patch('locpy.api.requests')
    def test_search(self, mockrequests):
        loc = LocAPI()
        mockrequests.codes = requests.codes
        # check that query with no results returns empty lists
        mock_result = {
            'q': 'notanentity*',
            'count': 0,
            'pagesize': 10,
            'start': 1,
            'sortmethod': 'rank',
            'searchtype': 'keyword',
            'directory': '/authorities/names/',
            'hits': [],
        }
        mockrequests.get.return_value.status_code = requests.codes.ok
        mockrequests.get.return_value.json.return_value = mock_result
        assert loc.search('notanentity', 'names') == []
        mockrequests.get.assert_called_with(
            'http://id.loc.gov/authorities/names/suggest2',
            params={'q': 'notanentity', 'searchtype': 'keyword'},
        )

        # test suggest results
        sru_fixture = os.path.join(FIXTURES_PATH, 'sru_search.json')
        with open(sru_fixture, encoding='utf-8') as srufile:
            mock_result = json.load(srufile)
        mockrequests.get.return_value.json.return_value = mock_result
        results = loc.search('Benjamin Franklin', 'names')
        assert isinstance(results, list)
        assert isinstance(results[0], SRUItem)
        mockrequests.get.assert_called_with(
            'http://id.loc.gov/authorities/names/suggest2',
            params={'q': 'Benjamin Franklin', 'searchtype': 'keyword'},
        )

        # bad status code should return empty list
        mockrequests.get.return_value.status_code = requests.codes.forbidden
        assert loc.search('test', 'names') == []


class TestLocEntity(object):
    # test entity from an unimplemented API
    test_id = 'mp2013015202'
    test_uri = 'http://id.loc.gov/authorities/mp2013015202'
    test_data_uri = 'http://id.loc.gov/authorities/performanceMediums/mp2013015202'
    rdf_fixture = os.path.join(FIXTURES_PATH, 'mp2013015202.rdf')

    def test_init(self):
        ent = LocEntity(self.test_id)
        assert ent.loc_id == self.test_id
        assert ent.uri == self.test_uri
        assert ent.dataset_uri == self.test_data_uri

    def test_uriref(self):
        ent = LocEntity(self.test_id)
        assert ent.uriref == rdflib.URIRef(self.test_uri)

    def test_dataset_uriref(self):
        ent = LocEntity(self.test_id)
        assert ent.dataset_uriref == rdflib.URIRef(self.test_data_uri)

    @patch('locpy.api.requests')
    @patch('locpy.api.rdflib')
    def test_rdf(self, mockrdflib, mockrequests):
        mock_codes = Mock()
        mock_codes.ok = 200
        mockrequests.codes = mock_codes
        mock_response = Mock()
        mock_response.status_code = mock_codes.ok
        mock_response.text = 'data'
        mockrequests.get.return_value = mock_response
        ent = LocEntity(self.test_id)
        assert ent.rdf == mockrdflib.Graph.return_value
        mockrdflib.Graph.assert_called_with()
        mockrequests.get.assert_called_with(
            self.test_uri, headers={'Accept': 'application/rdf+xml'}
        )
        mockrdflib.Graph.return_value.parse.assert_called_with(
            data=mock_response.text, format='xml'
        )

    def test_properties(self):
        ent = LocEntity(self.test_id)
        test_rdf = rdflib.Graph()
        test_rdf.parse(self.rdf_fixture)
        test_scheme = 'http://id.loc.gov/authorities/performanceMediums'
        test_instances = [
            'http://www.loc.gov/mads/rdf/v1#Medium',
            'http://www.loc.gov/mads/rdf/v1#Authority',
            'http://www.w3.org/2004/02/skos/core#Concept',
        ]

        # TODO: This logic is used a lot. Reconfigure as wrapper
        # patch fixture in to LocEntity rdf property
        with patch.object(LocEntity, 'rdf', new=test_rdf):
            assert str(ent.authoritative_label) == 'dancer'
            assert str(ent.scheme_membership) == test_scheme
            # construct plain list of instances
            instances = [str(i) for i in ent.instance_of]
            assert set(test_instances) == set(instances)


class TestNameEntity(object):
    loc_id = 'n79043402'
    test_rwo_uri = 'http://id.loc.gov/rwo/agents/n79043402'
    rdf_fixture = os.path.join(FIXTURES_PATH, 'n79043402.rdf')

    def test_get_rwo_uri(self):
        ent = NameEntity(self.loc_id)
        assert ent.rwo_uri == self.test_rwo_uri

    def test_rwo_uriref(self):
        ent = NameEntity(self.loc_id)
        assert ent.rwo_uriref == rdflib.URIRef(self.test_rwo_uri)

    def test_properties(self):
        ent = NameEntity(self.loc_id)
        test_rdf = rdflib.Graph()
        test_rdf.parse(self.rdf_fixture)

        # patch fixture in to NameEntity rdf property
        with patch.object(NameEntity, 'rdf', new=test_rdf):
            # test label to test when language is None
            assert str(ent.authoritative_label) == 'Franklin, Benjamin, 1706-1790'
            assert str(ent.birthdate) == '1706-01-17'
            assert str(ent.deathdate) == '1790-04-17'
            assert ent.birthyear == 1706
            assert ent.deathyear == 1790

    def test_year_from_edtf(self):
        assert NameEntity.year_from_edtf('1980') == 1980
        assert NameEntity.year_from_edtf('1980-01') == 1980
        assert NameEntity.year_from_edtf('2001-02-03') == 2001
        # test negative years
        assert NameEntity.year_from_edtf('-0468') == -468
        # test uncertainty markers in EDTF
        assert NameEntity.year_from_edtf('1847?') == 1847
        assert NameEntity.year_from_edtf('0213~') == 213


class TestSubjectEntity(object):
    def test_complex_entity(self):
        # Complex entities can have components that are either
        # name entities or subject entities
        rdf_fixture = os.path.join(FIXTURES_PATH, 'sh2008001841.rdf')

        ent = SubjectEntity('sh2008001841')
        test_rdf = rdflib.Graph()
        test_rdf.parse(rdf_fixture)

        with patch.object(SubjectEntity, 'rdf', new=test_rdf):
            assert len(ent.components) == 4
            names = [isinstance(c, NameEntity) for c in ent.components]
            subjects = [isinstance(c, SubjectEntity) for c in ent.components]
            assert names.count(True) == 1
            assert subjects.count(True) == 3

    def test_simple_entity(self):
        # Simple entities should not have components
        rdf_fixture = os.path.join(FIXTURES_PATH, 'sh85062079.rdf')
        ent = SubjectEntity('sh85062079')
        test_rdf = rdflib.Graph()
        test_rdf.parse(rdf_fixture)

        with patch.object(SubjectEntity, 'rdf', new=test_rdf):
            assert ent.components is None


def test_sru_result():
    sru_fixture = os.path.join(FIXTURES_PATH, 'sru_search.json')
    with open(sru_fixture, encoding='utf-8') as srufile:
        sru_data = json.load(srufile)
    sru_res = SRUResult(sru_data)
    assert sru_res.total_results == 10
    assert isinstance(sru_res.records, list)
    assert isinstance(sru_res.records[0], SRUItem)
    assert len(sru_res.records) == 10


def test_sru_item():
    sru_fixture = os.path.join(FIXTURES_PATH, 'sru_search.json')
    with open(sru_fixture, encoding='utf-8') as srufile:
        sru_data = json.load(srufile)
    sru_item = SRUResult(sru_data).records[0]
    assert sru_item.uri == 'http://id.loc.gov/authorities/names/nr91002273'
    assert sru_item.loc_id == 'nr91002273'
    assert sru_item.label == 'Joslin, Benjamin F. (Benjamin Franklin), 1796-1861'
