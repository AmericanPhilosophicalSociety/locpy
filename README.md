# locpy

[![unit tests](https://github.com/AmericanPhilosophicalSociety/locpy/actions/workflows/run-tests.yml/badge.svg)](https://github.com/AmericanPhilosophicalSociety/locpy/actions/workflows/run-tests.yml)

Python library for querying and representing LoC ID APIs. The library provides connectors for the Library of Congress Linked Data Authority.

locpy uses the python library rdflib to query Library of Congress entities and represent them as python classes.

### Supported search interfaces:
- [Resource retrieval](https://id.loc.gov/views/pages/swagger-api-docs/index.html#download.json) 
- [Known label retrieval](https://id.loc.gov/views/pages/swagger-api-docs/index.html#known-label-retrieval.json)
- [Left-anchored suggest](https://id.loc.gov/views/pages/swagger-api-docs/index.html#suggest-service-2.json)
- [Keyword query](https://id.loc.gov/views/pages/swagger-api-docs/index.html#suggest-service-2.json)

### Fully supported authorities:
- [LC Subject Headings](https://id.loc.gov/authorities/subjects.html)
- [LC Name Authority File](https://id.loc.gov/authorities/names.html)

### Partially supported authorities:
- [LC Children's Subject Headings](https://id.loc.gov/authorities/childrensSubjects.html)
- [LC Medium of Performance Thesaurus for Music](https://id.loc.gov/authorities/performanceMediums.html)
- [LC Demographic Group Terms](https://id.loc.gov/authorities/demographicTerms.html)
- [Thesaurus for Graphic Materials](https://id.loc.gov/vocabulary/graphicMaterials.html)
- [AFS Ethnographic Thesaurus](https://id.loc.gov/vocabulary/ethnographicTerms.html)
- [LC Genre/Form Terms](https://id.loc.gov/authorities/genreForms.html)

There are no plans to support further authorities at this point in time, but pull requests for implementations of other authorities are welcome!

## Installation

Via pip into virtual environment

Clone the repo, then in the base directory, run:

```$ pip install .```

## Usage

```
# construct URIs

>>>
>>> from locpy.api import LocAPI
>>> LocAPI.uri_from_id('n79043402')
'http://id.loc.gov/authorities/n79034903'

>>>
>>> LocAPI.dataset_uri_from_id('n79043402')
'http://id.loc.gov/authorities/names/n79043402'

# Query LoC search endpoints

>>>
>>> loc = LocAPI()
>>> loc.retrieve_label('Franklin, Benjamin, 1706-1790')
'n79043402'

# query the left-anchored search through the method "suggest"
# returns list of top ten results from API
>>>
>>> suggest = loc.suggest('Franklin, Benjamin')
>>> suggest[0].uri
'http://id.loc.gov/authorities/names/n2015067702'
>>> suggest[0].label
'Franklin Benjamin'

# method LocAPI.search() queries the keyword search method in the same manner

# Represent a single entity
>>>
>>> from locpy.api import LocEntity
>>> entity = LocEntity('mp2013015202')
>>> entity.authoritative_label
rdflib.term.Literal('dancer', lang='en')
>>> entity.dataset_uri
'http://id.loc.gov/authorities/performanceMediums/mp2013015202'
>>> entity.instance_of
[
    rdflib.term.URIRef('http://www.loc.gov/mads/rdf/v1#Medium'),
    rdflib.term.URIRef('http://www.loc.gov/mads/rdf/v1#Authority'),
    rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#Concept')
]

# Represent an entity from the Name Authority
>>>
>>> from locpy.api import NameEntity
>>> name = NameEntity('n79043402')
>>> name.authoritative_label
rdflib.term.Literal('Franklin, Benjamin, 1706-1790') # inherits all properties of LocEntity
>>> name.birthdate
rdflib.term.Literal('1706-01-17', datatype=rdflib.term.URIRef('http://id.loc.gov/datatypes/edtf/EDTF'))
>>> name.birthyear
1706
>>> name.deathdate
rdflib.term.Literal('1790-04-17', datatype=rdflib.term.URIRef('http://id.loc.gov/datatypes/edtf/EDTF'))
>>> name.deathyear
1790

# Represent an entity from the Subject Authority
>>>
>>> from locpy.api import SubjectEntity
>>> subject = SubjectEntity('sh85054401')
>>> subject.authoritative_label
rdflib.term.Literal('German literature--Germany (East)', lang='en') # inherits all properties of LocEntity
# for complex subjects, components instances of either NameEntity or SubjectEntity
>>> subject.components
[<locpy.api.SubjectEntity object at 0x0000025AF492B810>, <locpy.api.NameEntity object at 0x0000025AF492A990>]

```

## Running tests

Install development requirements  
```$ pip install -e ".[dev]"```

Run tests with pytest  
```$ python -m pytest```  
