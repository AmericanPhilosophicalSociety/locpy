from rdflib import Namespace
from urllib.parse import urljoin
from cached_property import cached_property

import rdflib
import requests


MADS_NS = Namespace('http://www.loc.gov/mads/rdf/v1#')


class LocAPI(object):
    """Wrapper for Library of Congress API.

    https://id.loc.gov/
    """

    # base url for URIs and API calls
    uri_base = 'http://id.loc.gov/authorities/'
    # Names Authorities base
    lcnaf_base = 'http://id.loc.gov/authorities/names/'
    # Subject Authorities base
    lcsh_base = 'http://id.loc.gov/authorities/subjects'
    # need to perform queries for RWO as well
    rwo_base = 'http://id.loc.gov/rwo/agents/'

    @classmethod
    def uri_from_id(cls, loc_id):
        '''Generate a URL for performing initial queries'''
        return urljoin(cls.uri_base, loc_id)

    @classmethod
    def dataset_uri_from_id(cls, loc_id):
        '''Generate a URI for RDF triples based on LoC dataset'''
        if loc_id.startswith('n'):
            return urljoin(cls.lcnaf_base, loc_id)
        elif loc_id.startswith('sh'):
            return urljoin(cls.lcsh_base, loc_id)
        else:
            # Throw error if URL malformed
            raise ValueError('''
            The ID does not conform to supported ID formats.
            Please verify the ID is correct.
            ''')

    @classmethod
    def rwo_uri_from_id(cls, loc_id):
        '''Generate RWO URI for linked data queries'''
        return urljoin(cls.rwo_base, loc_id)

    def suggest():
        '''Query LoC's suggest service API. Returns a list of
        results, or an empty list for no results or an error
        '''
        pass

    def search():
        pass


# Question: Does each dataset need its own representation?
class LocEntity(object):
    '''Object to represent single LoC entity

    :param loc_id: LoC identifier (string)
    '''

    def __init__(self, loc_id):
        # probably need to identify canonical ID from LoC dataset
        self.uri = LocAPI.uri_from_id(loc_id)
        self.rwo_uri = LocAPI.rwo_uri_from_id(loc_id)
        self.lcnaf_uri = LocAPI.dataset_uri_from_id(loc_id)

    @property
    def uriref(self):
        '''LoC URI reference as instance of :class: `rdflib.URIRef`'''
        return rdflib.URIRef(self.uri)

    @property
    def lcnaf_uriref(self):
        '''LoC URI reference that includes LCNAF dataset marker'''
        return rdflib.URIRef(self.lcnaf_uri)

    @property
    def rwo_uriref(self):
        '''LoC RWO URI reference as instance of :class: `rdflib.URIREF`'''
        return rdflib.URIRef(self.rwo_uri)

    @cached_property
    def rdf(self):
        '''LoC data for this entity as :class: `rdflib.Graph`'''
        graph = rdflib.Graph()
        response = requests.get(self.uri, headers={'Accept': 'application/rdf+xml'})
        response.raise_for_status()  # raise HTTPError on bad requests
        graph.parse(data=response.text, format="xml")

        return graph

    # person-specific properties

    @property
    def birthdate(self):
        '''MADS birthday as :class: `rdflib.term.Literal`'''
        return self.rdf.value(self.rwo_uriref, MADS_NS.birthDate)

    @property
    def deathdate(self):
        '''MADS deathdate as :class: `rdflib.term.Literal`'''
        return self.rdf.value(self.rwo_uriref, MADS_NS.deathDate)

    @property
    def birthyear(self):
        '''birth year as int'''
        if self.birthdate:
            return self.year_from_edtf(str(self.birthdate))

    @property
    def deathyear(self):
        '''death year as int'''
        if self.deathdate:
            return self.year_from_edtf(str(self.deathdate))

    @property
    def authoritative_label(self):
        '''Authoritative entity label in English'''
        labels = self.rdf.objects(
            self.lcnaf_uriref, MADS_NS.authoritativeLabel
        )
        # LoC only marks non-English language, so look for none
        # Need to make sure this is universally true
        for label in labels:
            if label.language is None:
                return label

    @classmethod
    def year_from_edtf(cls, date):
        '''Return just the year from EDTF date. Expects a string,
        returns an integer. Normalizes uncertain years. Supports
        negative dates. No support for partially unknown years.'''
        negative = False
        # if the date starts with a dash, flag negative and delete
        if date.startswith('-'):
            date = date[1:]
            negative = True
        # need more robust parsing here for approximate dates
        edtf_year = date.split('-')[0]
        edtf_chars = ['~', '?', '%']
        for c in edtf_chars:
            edtf_year = edtf_year.replace(c, '')
        edtf_year = int(edtf_year)
        if negative:
            return -edtf_year
        return edtf_year
