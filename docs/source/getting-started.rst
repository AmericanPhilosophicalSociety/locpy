Getting Started
===============

Installation
------------

Install locpy into a virtual environment with pip:

.. code-block:: console

    (.venv) $ pip install git+https://github.com/AmericanPhilosophicalSociety/locpy

Alternatively, install with uv:

.. code-block:: console

    $ uv add "locpy @git+https://github.com/AmericanPhilosophicalSociety/locpy"

Basic Usage
-----------

locpy can be used to construct URIs from known identifiers

>>> from locpy.api import LocAPI
>>> LocAPI.uri_from_id('n79043402')
'http://id.loc.gov/authorities/n79043402'
>>> LocAPI.dataset_uri_from_id('n79043402')
'http://id.loc.gov/authorities/names/n79043402'

You can also retrieve an identifier if you know the label

>>> loc = LocAPI()
>>> loc.retrieve_label('Franklin, Benjamin, 1706-1790')
'n79043402'

locpy provides support for querying the `"suggest" API`<https://id.loc.gov/views/pages/swagger-api-docs/index.html#suggest-service-2.json>_ provided by the Library of Congress. This performs a left-anchored search and will retrieve entries that start with the same character sequence as your query.

>>> suggest = loc.suggest('Franklin, Benjamin')
>>> suggest[0].uri
'http://id.loc.gov/authorities/names/n2015067702'
>>> suggest[0].label
'Franklin, Benjamin'

:meth:`LocAPI.search` queries the keyword search in the same manner. Both :meth:`LocAPI.search` and :meth:`LocAPI.suggest` accept an additional argument ``authority`` which lets you specify whether to query the Name Authority or Subject Header authority.

>>> search = loc.search('Benjamin Franklin', authority='names')
>>> search[0].uri
'http://id.loc.gov/authorities/names/nr91002273'
>>> search[0].label
'Joslin, Benjamin F. (Benjamin Franklin), 1796-1861'

locpy provides python classes that can represent single entities from the Linked Data Service

>>> from locpy.api import LocEntity
>>> entity = LocEntity('mp2013015202')
>>> entity.authoritative_label
rdflib.term.Literal('dancer', lang='en')
>>> entity.dataset_uri
'http://id.loc.gov/authorities/performanceMediums/mp2013015202'
>>> entity.instance_of
[rdflib.term.URIRef('http://www.loc.gov/mads/rdf/v1#Medium'), rdflib.term.URIRef('http://www.loc.gov/mads/rdf/v1#Authority'), rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#Concept')]

Additional wrappers are provided for the Name Authority and the Subject Authority. These subclass :class:`LocEntity` and inherit all its properties and methods, but contain additional properties to represent unique features of these authorities.

>>> from locpy.api import NameEntity
>>> name = NameEntity('n79043402')
>>> name.authoritative_label
rdflib.term.Literal('Franklin, Benjamin, 1706-1790')
>>> name.birthdate
rdflib.term.Literal('1706-01-17', datatype=rdflib.term.URIRef('http://id.loc.gov/datatypes/edtf'))
>>> name.birthyear
1706
>>> name.deathdate
rdflib.term.Literal('1790-04-17', datatype=rdflib.term.URIRef('http://id.loc.gov/datatypes/edtf'))
>>> name.deathyear
1790

Complex topics list their components as instances of either :class:`NameEntity` or :class:`SubjectEntity`

>>> from locpy.api import SubjectEntity
>>> subject = SubjectEntity('sh85054401')
>>> subject.authoritative_label
rdflib.term.Literal('German literature--Germany (East)', lang='en')
>>> [type(s) for s in subject.components]
[<class 'locpy.api.SubjectEntity'>, <class 'locpy.api.NameEntity'>]
