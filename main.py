from collections import defaultdict
import os
import json
import uuid
from rdflib.namespace import DCTERMS

from rdflib.term import BNode

from eadParser import parseEAD
from pya2a import DocumentCollection as A2ADocumentCollection

from rdflib import Dataset, Namespace, Literal, XSD, RDF, RDFS, URIRef
from rdfalchemy import rdfSubject

import rdflib.graph
from model import *

ga = Namespace("https://data.goldenagents.org/datasets/")
rdflib.graph.DATASET_DEFAULT_GRAPH_ID = ga

INDICES = [("08953f2f-309c-baf9-e5b1-0cefe3891b37",
            "SAA-ID-001_SAA_Index_op_notarieel_archief"),
           ("f6e5401f-c486-5f3d-6a5c-6e277e12628e",
            "SAA-ID-002_SAA_Index_op_doopregisters"),
           ("2f352e18-256e-b4d1-e74f-3ffaf5e633f1",
            "SAA-ID-003_SAA_Index_op_ondertrouwregisters"),
           ("47828428-360d-afdd-1f07-2c13e34635e1",
            "SAA-ID-004_SAA_Index_op_kwijtscheldingen"),
           ("23d6fddb-4839-f080-2b0a-05a21c6162e8",
            "SAA-ID-005_SAA_Index_op_poorterboeken"),
           ("c53f836b-d7f0-fcd0-fc99-09192ccb17ad",
            "SAA-ID-006_SAA_Index_op_confessieboeken"),
           ("d46628d6-2ed4-95a0-cafc-4cdbb4174263",
            "SAA-ID-007-SAA_Index_op_boetes_op_trouwen_en_begraven"),
           ("9823b7a8-ab79-a098-4ab0-26e799ea5659",
            "SAA-ID-008_SAA_Index_op_begraafregisters_voor_1811")]

# type2uri = {
#     'other: T
# }

with open('data/uri2notary.json') as infile:
    uri2notary = json.load(infile)

    uri2notary = {
        URIRef(k): [URIRef(i) for i in v]
        for k, v in uri2notary.items()
    }


def unique(*args):
    """Function to generate a unique BNode based on a series of arguments.

    Uses the uuid5 function to generate a uuid from one or multiple ordered 
    arguments. This way, the BNode function of rdflib can be used, without the 
    need to filter strange characters or spaces that will break the serialization. 

    Returns:
        BNode: Blank node with identifier that is based on the function's input.
    """

    identifier = "".join(str(i) for i in args)  # order matters

    unique_id = uuid.uuid5(uuid.NAMESPACE_X500, identifier)

    return BNode(unique_id)


def bindNS(g):

    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)
    g.bind('roar', roar)
    g.bind('pnv', pnv)
    g.bind('sem', sem)
    g.bind('dcterms', DCTERMS)
    g.bind('file', 'https://archief.amsterdam/inventarissen/file/')

    return g


def main(eadfolder="data/ead",
         a2afolder="data/a2a",
         outfile='roar.trig',
         splitFile=True,
         splitSize=100):

    ds = Dataset()

    identifier2book = defaultdict(dict)

    # EAD
    print("EAD parsing!")
    g = rdfSubject.db = ds.graph(identifier=ga.term('saa/ead/'))
    for dirpath, dirname, filenames in os.walk(eadfolder):
        for n, f in enumerate(sorted(filenames), 1):
            print(f"{n}/{len(filenames)} {f}")
            if f.endswith('.xml') and '5001' in f:
                identifier2book = convertEAD(os.path.join(dirpath, f),
                                             g,
                                             identifier2book=identifier2book)
            else:
                continue

            if splitFile:
                path = f"trig/{f}.trig"
                print("Serializing to", path)

                g = bindNS(g)
                g.serialize(path, format='trig')
                ds.remove_graph(g)
                g = rdfSubject.db = ds.graph(identifier=ga.term('saa/ead/'))

    # A2A
    print("A2A parsing!")
    g = rdfSubject.db = ds.graph(identifier=ga.term('saa/a2a/'))
    for dirpath, dirname, filenames in os.walk(a2afolder):
        nSplit = 0
        for n, f in enumerate(sorted(filenames),
                              1):  # test on 20 files per index
            if f.endswith('.xml') and 'ondertrouw' in dirpath:
                path = os.path.abspath(os.path.join(dirpath, f))
                convertXML(path, ds, identifier2book)
            else:
                continue

            if splitFile and (n % splitSize == 0 or n == len(filenames)):
                nSplit += 1

                foldername = dirpath.rsplit('/')[-1]
                path = f"trig/{foldername}_{str(nSplit).zfill(4)}.trig"
                print("Serializing to", path)

                g = bindNS(g)
                g.serialize(path, format='trig')
                ds.remove_graph(g)
                g = rdfSubject.db = ds.graph(identifier=ga.term('saa/a2a/'))

    # HTR
    #print("HTR parsing!")
    g = rdfSubject.db = ds.graph(identifier=ga.term('saa/htr/'))

    ## Finished!

    ds = bindNS(ds)

    if not splitFile:
        print(f'Serializing to {outfile}')
        ds.serialize('trig/roar.trig', format='trig')
    else:
        # ontology only
        g = rdfSubject.db = ds.graph(identifier=roar)
        g.serialize('trig/roar.trig', format='trig')


def convertEAD(xmlfile, g, identifier2book=defaultdict(dict)):

    ead = parseEAD(xmlfile)

    c = ead.collection[0]

    uri = URIRef(f"https://archief.amsterdam/inventarissen/file/{c.id}")
    collection, identifier2book = getCollection(
        c, uri, identifier2book=identifier2book)  # top collection

    return identifier2book


def cToRdf(c,
           identifier2book,
           parent=None,
           collectionNumber=None,
           scanNamespace=None):

    # if collectionNumber:
    #     saaCollection = Namespace(
    #         f"https://data.goldenagents.org/datasets/SAA/{collectionNumber}/")
    # else:
    #     saaCollection = ga

    uri = URIRef(f"https://archief.amsterdam/inventarissen/file/{c.id}")

    if c.level == 'file':
        # Then this is a book --> InventoryBook

        collection = Book(uri,
                          label=[c.name] if c.name else [c.identifier],
                          description=[c.description] if c.description else [],
                          identifier=c.identifier,
                          temporal=c.date.get('temporal'))
        # hasTimeStamp=c.date.get('hasTimeStamp'),
        # hasBeginTimeStamp=c.date.get('hasBeginTimeStamp'),
        # hasEndTimeStamp=c.date.get('hasEndTimeStamp'),
        # hasEarliestBeginTimeStamp=c.date.get('hasEarliestBeginTimeStamp'),
        # hasLatestBeginTimeStamp=c.date.get('hasLatestBeginTimeStamp'),
        # hasEarliestEndTimeStamp=c.date.get('hasEarliestEndTimeStamp'),
        # hasLatestEndTimeStamp=c.date.get('hasLatestEndTimeStamp'))

        return collection, 'file', identifier2book

    else:
        # Not yet reached the end of the tree
        if parent and parent.resUri != URIRef(
                "https://archief.amsterdam/inventarissen/file/d5b98b7afa50a3af4fba8053b06fb961"
        ):  # these ids in the middle are not unique
            uri = None

        collection, identifier2book = getCollection(
            c, uri, identifier2book=identifier2book)

        return collection, 'collection', identifier2book


def getCollection(c, uri, identifier2book=defaultdict(dict)):

    collection = DocumentCollection(
        uri,
        label=[c.name] if c.name else [c.identifier],
        description=[c.description] if c.description else [],
        identifier=c.identifier,
        temporal=c.date.get('temporal'))

    if hasattr(c, 'language'):
        language = [c.language]
        collection.language = language
    else:
        language = []

    repositories = []
    if hasattr(c, 'repository'):
        if type(c.repository) != list:
            repository = [c.repository]
        else:
            repository = c.repository

        for i in repository:
            if 'corpname' in c.repository:
                name = c.repository['corpname']
                repository = Agent(unique(name), label=[name])
            else:
                repository = c.repository
            repositories.append(repository)

    collection.repository = repositories

    originations = []
    if hasattr(c, 'origination'):
        if type(c.origination) != list:
            origination = [c.origination]
        else:
            origination = c.origination

        for i in origination:
            if 'corpname' in i:
                name = i['corpname']
                org = Agent(unique(name), label=[name])
            else:
                org = i
            originations.append(org)

    if uri2notary.get(uri):  # specifically for collection 5075
        for n in uri2notary[uri]:
            originations.append(Agent(n))

    collection.origination = originations

    groupingCriteria = getGroupingCriteria(sourceType=[roar.Inventory],
                                           sourceDate=c.date,
                                           sourceAuthor=originations,
                                           sourceLanguage=language)
    collection.hasGroupingCriteria = groupingCriteria

    subcollections = []
    parts = []
    for ch in c.children:
        ch, chtype, identifier2book = cToRdf(ch,
                                             identifier2book,
                                             parent=collection)

        if chtype == 'collection':
            subcollections.append(ch)
        elif chtype == 'file':
            parts.append(ch)

    collection.hasSubCollection = subcollections
    collection.hasMember = parts

    # Creation event

    allUris, allIdentifiers = getAllChildren(c)
    collectionIdentifier = getParentIdentifier(c)

    for u, i in zip(allUris, allIdentifiers):
        identifier2book[collectionIdentifier][i] = u

    creationEvent = CollectionCreation(None,
                                       hasInput=allUris,
                                       hasOutput=[collection])

    archiverRole = ArchiverAndCreatorRole(None,
                                          carriedIn=creationEvent,
                                          carriedBy=repositories)

    archivalDocumentRole = ArchivalDocumentRole(None,
                                                carriedIn=creationEvent,
                                                carriedBy=[collection])

    return collection, identifier2book


def getAllChildren(c):

    uris = []
    identifiers = []
    for child in c.children:
        if child.level == 'file':
            uris.append(
                URIRef(
                    f"https://archief.amsterdam/inventarissen/file/{child.id}")
            )
            identifiers.append(child.identifier)
        else:
            urisNew, identifiersNew = getAllChildren(child)
            uris += urisNew
            identifiers += identifiersNew

    return uris, identifiers


def getParentIdentifier(c):

    if hasattr(c, 'parent'):
        identifier = getParentIdentifier(c.parent)
    else:
        identifier = c.identifier
    return identifier


def getGroupingCriteria(sourceType=[],
                        sourceDate=dict(),
                        sourceAuthor=[],
                        sourceLanguage=None):

    criteria = []

    if sourceType:
        criterion = GroupingCriterion(None,
                                      hasFilter=roar.sourceType,
                                      hasFilterValue=sourceType)
        criteria.append(criterion)

    if sourceDate:

        start = sourceDate.get('hasEarliestBeginTimeStamp')
        end = sourceDate.get('hasLatestEndTimeStamp')

        criterion = GroupingCriterion(None,
                                      hasFilter=roar.createdAt,
                                      hasFilterStart=start,
                                      hasFilterEnd=end)
        criteria.append(criterion)

    if sourceAuthor:
        criterion = GroupingCriterion(None,
                                      hasFilter=roar.createdBy,
                                      hasFilterValue=sourceAuthor)
        criteria.append(criterion)

    if sourceLanguage:
        criterion = GroupingCriterion(None,
                                      hasFilter=roar.createdBy,
                                      hasFilterValue=sourceLanguage)
        criteria.append(criterion)

    return criteria


def convertXML(xmlfile, ds, identifier2book):
    c = A2ADocumentCollection(xmlfile)

    for d in c:

        collection = d.source.SourceReference.Archive
        inventory = d.source.SourceReference.RegistryNumber
        partOfUri = URIRef(identifier2book[collection][inventory])

        createdByUris = []
        if uri2notary.get(partOfUri):  # specifically for collection 5075
            for n in uri2notary[partOfUri]:
                createdByUris.append(Agent(n))

        if hasattr(d.source, 'SourceDate'):
            createdAtDate = d.source.SourceDate.date
        else:
            createdAtDate = None

        # source
        source = Document(a2a.term(d.source.guid),
                          label=[d.source.SourceType],
                          partOf=partOfUri,
                          createdBy=createdByUris,
                          createdAt=createdAtDate)

        # events
        events = []
        for e in d.events:

            eventTypeName = e.EventType.replace('other: ',
                                                '').title().replace(' ', '')

            # Switch to ontology graph
            g = rdfSubject.db = ds.graph(identifier=roar)
            EventClass = type(e.EventType, (Event, ),
                              {"rdf_type": roar.term(eventTypeName)})

            eType = EventType(roar.term(eventTypeName),
                              subClassOf=roar.Event,
                              label=[eventTypeName])

            # Switch to A2A graph
            g = rdfSubject.db = ds.graph(identifier=a2a)

            if e.EventDate and e.EventDate.date:
                eventDate = e.EventDate.date
            else:
                eventDate = None

            event = EventClass(
                a2a.term(d.source.guid + '#' + e.id),
                hasTimeStamp=eventDate,
                label=[
                    f"{eventTypeName} ({eventDate.isoformat() if eventDate else '?'})"
                ])
            events.append(event)

        # persons and roles
        for p in d.persons:

            pn = PersonName(
                None,
                givenName=p.PersonName.PersonNameFirstName,
                surnamePrefix=p.PersonName.PersonNamePrefixLastName,
                baseSurname=p.PersonName.PersonNameLastName)

            label = " ".join([i for i in p.PersonName])
            pn.label = label
            pn.literalName = label

            person = Person(a2a.term(d.source.guid + '#' + p.id),
                            participatesIn=events,
                            hasName=[pn],
                            label=[label])

            for r in p.relations:
                if e := getattr(r, 'event'):

                    relationTypeName = r.RelationType.replace(
                        'other: ', '').title().replace(' ', '')

                    # Switch to ontology graph
                    g = rdfSubject.db = ds.graph(identifier=roar)
                    RoleClass = type(r.RelationType, (Role, ),
                                     {"rdf_type": roar.term(relationTypeName)})

                    rType = RoleType(roar.term(r.RelationType),
                                     subClassOf=roar.Role,
                                     label=[r.RelationType])

                    # Switch to A2A graph
                    g = rdfSubject.db = ds.graph(identifier=a2a)
                    eUri = a2a.term(d.source.guid + '#' + e.id)
                    role = RoleClass(None,
                                     carriedIn=eUri,
                                     carriedBy=[person],
                                     label=[r.RelationType])

            # # Remarks
            # for remark in p.Remarks['diversen']:
            #     if remark == 'Adres':
            #         adres = p.Remarks['diversen']['Adres']
            #         locObs = LocationObservation(safeBnode(adres),
            #                                      label=[adres])

            #         person.hasLocation = [
            #             StructuredValue(None,
            #                             value=locObs,
            #                             role="resident",
            #                             hasLatestBeginTimeStamp=eventDate,
            #                             hasEarliestEndTimeStamp=eventDate)
            #         ]


if __name__ == "__main__":
    main()