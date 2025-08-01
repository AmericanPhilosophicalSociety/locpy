from locpy.api import LocAPI

import pytest


class TestLocAPI(object):
    def test_get_uri(self):
        assert LocAPI.uri_from_id("n79043402") == "http://id.loc.gov/authorities/n79043402"

    def test_get_rwo_uri(self):
        assert LocAPI.rwo_uri_from_id("n79043402") == "http://id.loc.gov/rwo/agents/n79043402"

    def test_get_lcnaf_uri(self):
        assert LocAPI.dataset_uri_from_id("n79043402") == "http://id.loc.gov/authorities/names/n79043402"

    def test_get_lcsh_uri(self):
        assert LocAPI.datast_uri_from_id("sh85100849") == "http://id.loc.gov/authorities/subjects/sh85100849"

    def test_not_lcsh_err(self):
        with pytest.raises(ValueError):
            LocAPI.dataset_uri_from_id('TR658.3')
