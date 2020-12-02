import multiprocessing

import os
import json
import uuid
import unidecode
from collections import defaultdict

from eadParser import parseEAD
from pya2a import DocumentCollection as A2ADocumentCollection

from rdflib import Dataset, Namespace, Literal, BNode, XSD, RDF, RDFS, URIRef, DCTERMS
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

# Global dictionaries
identifier2book = defaultdict(dict)
identifier2physicalBook = defaultdict(dict)

with open('data/uri2notary.json') as infile:
    uri2notary = json.load(infile)

    uri2notary = {
        URIRef(k): [URIRef(i) for i in v]
        for k, v in uri2notary.items()
    }

with open('data/scanid2name_5075.json') as infile:
    scanid2name = json.load(infile)


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


def thesaurus(name, ClassType, defaultGraph, thesaurusGraph):

    if not name:
        return None

    namenorm = unidecode.unidecode(name)
    namenorm = namenorm.title()
    namenorm = "".join(
        [i for i in namenorm if i.lower() in 'abcdefghijklmnopqrstuvwxyz'])

    if not namenorm:  # if no characters are left
        return None

    g = rdfSubject.db = thesaurusGraph

    uri = ClassType(thes.term(namenorm), label=[name])

    g = rdfSubject.db = defaultGraph  # restore graph

    return uri


def bindNS(g):

    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)
    g.bind('roar', roar)
    g.bind('pnv', pnv)
    g.bind('sem', sem)
    g.bind('dcterms', DCTERMS)
    g.bind('file', file)
    g.bind('foaf', foaf)
    g.bind('oa', oa)

    return g


def main(eadfolder="data/ead",
         a2afolder="data/a2a",
         outfile='roar.trig',
         splitFile=True,
         splitSize=100):

    ds = Dataset()

    # EAD
    print("EAD parsing!")
    g = rdfSubject.db = ds.graph(identifier=ga.term('saa/ead/'))
    for dirpath, dirname, filenames in os.walk(eadfolder):
        for n, f in enumerate(sorted(filenames), 1):
            print(f"{n}/{len(filenames)} {f}")
            if f.endswith('.xml'):
                convertEAD(os.path.join(dirpath, f), g)
            else:
                continue

            if splitFile:
                path = f"trig/{f}.trig"
                g = bindNS(g)

                print("Serializing to", path)
                # g.serialize(path, format='trig')
                ds.remove_graph(g)
                g = rdfSubject.db = ds.graph(identifier=ga.term('saa/ead/'))

    # with open('data/concordance/identifier2physicalBook.json', 'w') as outfile:
    #     json.dump(identifier2physicalBook, outfile)

    # return

    # A2A
    print("A2A parsing!")
    g = rdfSubject.db = ds.graph(identifier=ga.term('saa/a2a/'))
    for dirpath, dirname, filenames in os.walk(a2afolder):

        # # DTB
        # if 'doop' not in dirpath and 'trouw' not in dirpath and 'begraaf' not in dirpath:
        #     continue

        # Notarieel
        if 'nota' not in dirpath:
            continue

        nSplit = 0
        filenames = [
            os.path.abspath(os.path.join(dirpath, i))
            for i in sorted(filenames) if i.endswith('.xml')
        ][:1]

        chunks = []
        foldername = dirpath.rsplit('/')[-1]
        fns = []
        for n, f in enumerate(filenames, 1):
            fns.append(f)

            if n % splitSize == 0 or n == len(filenames):
                nSplit += 1
                path = f"trig/{foldername}_{str(nSplit).zfill(4)}.trig"
                chunks.append((fns, path))
                fns = []

        with multiprocessing.Pool(processes=10) as pool:

            graphs = pool.starmap(convertA2A, chunks)

        for og, tg in graphs:
            ontologyGraph = ds.graph(identifier=roar)
            thesaurusGraph = ds.graph(identifier=thes)
            ontologyGraph += og
            thesaurusGraph += tg

        # for n, f in enumerate(filenames, 1):

        #     path = os.path.abspath(os.path.join(dirpath, f))
        #     convertA2A(path, ds)

        #     if splitFile and (n % splitSize == 0 or n == len(filenames)):
        #         nSplit += 1

        #
        #         path = f"trig/{foldername}_{str(nSplit).zfill(4)}.trig"
        #         print("Serializing to", path)

        #         g = bindNS(g)
        #         g.serialize(path, format='trig')
        #         ds.remove_graph(g)
        #         g = rdfSubject.db = ds.graph(identifier=ga.term('saa/a2a/'))

    # HTR
    #print("HTR parsing!")
    g = rdfSubject.db = ds.graph(identifier=ga.term('saa/htr/'))

    ## Finished!

    ds = bindNS(ds)

    if not splitFile:
        print(f'Serializing to {outfile}')
        ds.serialize('trig/roar.trig', format='trig')
    else:
        # ontology
        g = rdfSubject.db = ds.graph(identifier=roar)
        g.serialize('trig/roar.trig', format='trig')

        # thesaurus
        g = rdfSubject.db = ds.graph(identifier=thes)
        g.serialize('trig/thesaurus.trig', format='trig')


def convertEAD(xmlfile, g):

    eadDocument = parseEAD(xmlfile)

    c = eadDocument.collection[0]

    uri = URIRef(f"https://archief.amsterdam/inventarissen/file/{c.id}")
    physicalUri = ead.term(c.id)

    # top collection, create a physical collection
    getCollection(c, uri, physicalUri=physicalUri)


def cToRdf(c, parent=None, collectionNumber=None, scanNamespace=None):

    uri = URIRef(f"https://archief.amsterdam/inventarissen/file/{c.id}")

    if c.level == 'file':
        # Then this is a book --> InventoryBook

        if c.name:
            label = [Literal(c.name, lang='nl')]
        else:
            label = [Literal(f"Inventaris {c.identifier}", lang='nl')]

        indexBook = IndexBook(
            uri,
            label=label,
            description=[c.description] if c.description else [],
            identifier=c.identifier,
            temporal=c.date.get('temporal'))

        physicalBook = InventoryBook(ead.term(c.id),
                                     createdBy=uri2notary.get(uri, []),
                                     createdAt=TimeInterval(None,
                                                            start=None,
                                                            end=None))

        indexBook.indexOf = physicalBook

        creationEvent = DocumentCreation(
            ead.term(f"{c.id}#creation"),
            hasInput=[],
            hasOutput=[physicalBook],
            hasTimeStamp=c.date.get('hasTimeStamp'),
            hasBeginTimeStamp=c.date.get('hasBeginTimeStamp'),
            hasEndTimeStamp=c.date.get('hasEndTimeStamp'),
            hasEarliestBeginTimeStamp=c.date.get('hasEarliestBeginTimeStamp'),
            hasLatestBeginTimeStamp=c.date.get('hasLatestBeginTimeStamp'),
            hasEarliestEndTimeStamp=c.date.get('hasEarliestEndTimeStamp'),
            hasLatestEndTimeStamp=c.date.get('hasLatestEndTimeStamp'))

        if notaryUris := uri2notary.get(uri, []):
            for notaryUri in notaryUris:
                notaryRole = NotaryRole(None,
                                        carriedIn=creationEvent,
                                        carriedBy=[notaryUri])

                Agent(notaryUri).participatesIn = [creationEvent]

        creationIndexEvent = DocumentCreation(
            ead.term(f"{c.id}#indexCreation"),
            hasInput=[physicalBook],
            hasOutput=[indexBook])

        return indexBook, physicalBook, 'file'

    else:
        # Not yet reached the end of the tree
        if parent and parent.resUri != URIRef(
                "https://archief.amsterdam/inventarissen/file/d5b98b7afa50a3af4fba8053b06fb961"
        ):  # these ids in the middle are not unique
            uri = None

        collection = getCollection(c, uri)

        return collection, None, 'collection'


def getCollection(c, uri, physicalUri=None):

    collection = IndexCollection(
        uri,
        label=[c.name] if c.name else [c.identifier],
        description=[c.description] if c.description else [],
        identifier=c.identifier,
        temporal=c.date.get('temporal'))

    if hasattr(c, 'language'):
        language = [c.language]
        collection.language = language  # find dcterm alternative + iso
    else:
        language = []

    repositories = []
    authorities = []
    if hasattr(c, 'repository'):
        if type(c.repository) != list:
            repository = [c.repository]
        else:
            repository = c.repository

        for i in repository:
            if 'corpname' in c.repository:
                name = c.repository['corpname']
                repository = Agent(unique(name), label=[name])
                authority = name
            else:
                repository = c.repository
                authority = c.repository
            authorities.append(authority)
            repositories.append(repository)

    collection.authority = authorities

    originations = []
    creators = []
    if hasattr(c, 'origination'):
        if type(c.origination) != list:
            origination = [c.origination]
        else:
            origination = c.origination

        for i in origination:
            if 'corpname' in i:
                name = i['corpname']
                org = Agent(unique(name), label=[name])
                creator = name
            else:
                org = i
                creator = i
            creators.append(creator)
            originations.append(org)

    if uri2notary.get(uri):  # specifically for collection 5075
        for n in uri2notary[uri]:
            originations.append(Agent(n))

    collection.creator = creators

    groupingCriteria = getGroupingCriteria(sourceType=[roar.Inventory],
                                           sourceDate=c.date,
                                           sourceAuthor=originations,
                                           sourceLanguage=language)
    collection.hasGroupingCriteria = groupingCriteria

    subcollections = []
    parts = []
    for ch in c.children:
        chIndex, chPhysical, chtype = cToRdf(ch, parent=collection)

        if chtype == 'collection':
            subcollections.append(chIndex)
        elif chtype == 'file':
            parts.append(chIndex)

    collection.hasSubCollection = subcollections
    collection.hasMember = parts

    # Creation event

    allUris, allIdentifiers = getAllChildren(c, ns=file)
    allUrisPhysical, allIdentifiersPhysical = getAllChildren(c, ns=ead)
    collectionIdentifier = getParentIdentifier(c)

    for u, i in zip(allUris, allIdentifiers):
        identifier2book[collectionIdentifier][i] = u

    for u, i in zip(allUrisPhysical, allIdentifiersPhysical):
        identifier2physicalBook[collectionIdentifier][i] = u

    creationEvent = CollectionCreation(None,
                                       hasInput=allUris,
                                       hasOutput=[collection])

    archiverRole = ArchiverAndCreatorRole(None,
                                          carriedIn=creationEvent,
                                          carriedBy=repositories)

    archivalDocumentRole = ArchivalDocumentRole(None,
                                                carriedIn=creationEvent,
                                                carriedBy=[collection])

    if physicalUri:
        physicalCollection = InventoryCollection(physicalUri,
                                                 hasMember=allUrisPhysical)
        collection.indexOf = physicalCollection

        return collection, physicalCollection
    else:
        return collection


def getAllChildren(c, ns):

    uris = []
    identifiers = []
    for child in c.children:
        if child.level == 'file':
            uris.append(ns.term(child.id))
            identifiers.append(child.identifier)
        else:
            urisNew, identifiersNew = getAllChildren(child, ns=ns)
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

    if sourceLanguage:  # iso code?
        criterion = GroupingCriterion(None,
                                      hasFilter=roar.language,
                                      hasFilterValue=sourceLanguage)
        criteria.append(criterion)

    return criteria


def convertA2A(filenames, path):

    ontologyGraph = Graph(identifier=roar)
    thesaurusGraph = Graph(identifier=thes)
    graph = Graph(identifier=a2a)

    #     path = os.path.abspath(os.path.join(dirpath, f))
    #     convertA2A(path, ds)

    #     if splitFile and (n % splitSize == 0 or n == len(filenames)):
    #         nSplit += 1

    #         foldername = dirpath.rsplit('/')[-1]
    #         path = f"trig/{foldername}_{str(nSplit).zfill(4)}.trig"
    #         print("Serializing to", path)

    #         g = bindNS(g)
    #         g.serialize(path, format='trig')
    #         ds.remove_graph(g)
    #         g = rdfSubject.db = ds.graph(identifier=ga.term('saa/a2a/'))

    for xmlfile in filenames:

        c = A2ADocumentCollection(xmlfile)

        for d in c:

            collection = d.source.SourceReference.Archive
            inventory = d.source.SourceReference.RegistryNumber
            partOfUri = identifier2physicalBook[collection][inventory]
            partOfIndexUri = identifier2book[collection][inventory]

            createdByUris = []
            if creators := uri2notary.get(
                    partOfIndexUri):  # specifically for collection 5075
                for n in creators:
                    createdByUris.append(Agent(n))

            if hasattr(d.source, 'SourceDate'):
                createdAtDate = d.source.SourceDate.date
            else:
                createdAtDate = None

            if hasattr(d.source, 'SourcePlace'):
                name = d.source.SourcePlace.Place
                createdInPlace = thesaurus(name, Place, graph, thesaurusGraph)
            else:
                createdInPlace = None

            # source remarks
            try:
                if comment := d.source.Remarks['Opmerking']['Opmerking']:
                    comments = [Literal(comment, lang='nl')]  # otr
                else:
                    comments = []
            except:
                comments = []

            try:
                if comment := d.source.Remarks['Opmerking'][
                        'Relatie informatie']:
                    comments = [Literal(comment, lang='nl')]  # begraaf
                else:
                    comments = []
            except:
                comments = []

            # source

            sourceTypeName = d.source.SourceType.lower().replace(
                'other: ', '').title().replace(' ', '')

            # Switch to ontology graph
            g = rdfSubject.db = ontologyGraph
            SourceClass = type(d.source.SourceType, (Document, ),
                               {"rdf_type": roar.term(sourceTypeName)})

            sType = DocumentType(roar.term(sourceTypeName),
                                 subClassOf=roar.Document,
                                 label=[sourceTypeName])

            # Switch to A2A graph
            g = rdfSubject.db = graph

            # Physical deed
            physicalUri = partOfUri + '#' + d.source.guid
            source = SourceClass(physicalUri,
                                 partOf=partOfUri,
                                 createdBy=createdByUris,
                                 createdAt=createdAtDate,
                                 createdIn=createdInPlace)

            # Index document
            indexUri = deed.term(d.source.guid)
            sourceIndex = IndexDocument(indexUri,
                                        label=[sourceTypeName],
                                        description=comments,
                                        indexOf=source)

            ## scans
            scans = []

            for n, scan in enumerate(d.source.scans, 1):

                identifier = scan.Uri.rsplit('/')[-1].replace('.jpg', '')
                if label := scanid2name.get(identifier, []):
                    label = [label.upper()]

                    scanUri = partOfUri + '#' + identifier
                else:
                    scanUri = deed.term(
                        d.source.guid
                    ) + '?scan=' + scan.OrderSequenceNumber.zfill(3)

                s = Scan(scanUri,
                         identifier=identifier,
                         label=label,
                         depiction=[URIRef(scan.Uri)])
                scans.append(s)

            # scanCollection = ScanCollection(None, hasMember=scans)

            # events
            events = []
            for e in d.events:

                eventTypeName = e.EventType.lower().replace(
                    'other: ', '').title().replace(' ', '')

                # Switch to ontology graph
                g = rdfSubject.db = ontologyGraph
                EventClass = type(e.EventType, (Event, ),
                                  {"rdf_type": roar.term(eventTypeName)})

                eType = EventType(roar.term(eventTypeName),
                                  subClassOf=roar.Event,
                                  label=[eventTypeName])

                # Switch to A2A graph
                g = rdfSubject.db = graph

                if e.EventDate and e.EventDate.date:
                    eventDate = e.EventDate.date
                else:
                    eventDate = None

                # eventPlace for begraaf + doop
                if eventTypeName == 'Begraven':
                    if type(d.source.Remarks['Opmerking']) != str:
                        eventPlaceName = d.source.Remarks['Opmerking'].get(
                            'Begraafplaats')
                        eventPlace = thesaurus(eventPlaceName, Place, graph,
                                               thesaurusGraph)
                    else:
                        eventPlace = None
                elif eventTypeName == 'Doop':
                    if type(d.source.Remarks['Opmerking']) != str:
                        eventPlaceName = d.source.Remarks['Opmerking'].get(
                            'Kerk')
                        eventPlace = thesaurus(eventPlaceName, Place, graph,
                                               thesaurusGraph)
                    else:
                        eventPlace = None
                else:
                    eventPlace = None

                # religion
                if hasattr(e, 'EventReligion'):
                    eventReligion = thesaurus(e.EventReligion, Religion, graph,
                                              thesaurusGraph)
                else:
                    eventReligion = None

                event = EventClass(
                    deed.term(d.source.guid + '?event=' + e.id),
                    occursAt=eventPlace,
                    religion=eventReligion,
                    hasTimeStamp=eventDate,
                    label=[
                        f"{eventTypeName} ({eventDate.isoformat() if eventDate else '?'})"
                    ])
                events.append(event)

            # persons and roles
            persons = []
            for n, p in enumerate(d.persons, 1):

                pn = PersonName(
                    None,
                    givenName=p.PersonName.PersonNameFirstName,
                    surnamePrefix=p.PersonName.PersonNamePrefixLastName,
                    baseSurname=p.PersonName.PersonNameLastName)

                pLabel = " ".join([i for i in p.PersonName])
                pn.label = pLabel
                pn.literalName = pLabel

                ## Annotation PersonName on scan (Notarial)

                if hasattr(p, 'Remarks'):
                    if scanData := p.Remarks.get('diversen'):
                        scanName = scanData['Positie op scan']['scan']
                        scanPosition = scanData['Positie op scan']['positie']
                        coordinates = scanPosition.replace(' ', '')

                        an = Annotation(
                            None,
                            hasBody=pn,
                            hasTarget=SpecificResource(
                                None,
                                hasSource=scanName,  #TODO
                                hasSelector=FragmentSelector(
                                    None,
                                    conformsTo=URIRef(
                                        "http://www.w3.org/TR/media-frags/"),
                                    value=coordinates)),
                            # depiction=depiction,
                            label=[pLabel])

                ##

                person = Person(deed.term(d.source.guid + '?person=' +
                                          p.id.replace("Person:", '')),
                                participatesIn=events,
                                hasName=[pn],
                                label=[pLabel])

                # birth in A2A defined
                if bd := getattr(p, 'BirthDate'):

                    birthDate = bd.date
                    birthLabel = [
                        Literal(
                            f"Geboorte van {pLabel} ({birthDate.toisoformat() if birthDate else '?'})"
                        )
                    ]

                    birthEvent = Geboorte(deed.term(d.source.guid +
                                                    '?event=birth'),
                                          hasTimeStamp=birthDate,
                                          label=birthLabel)

                    role = ChildRole(None,
                                     carriedIn=birthEvent,
                                     carriedBy=person,
                                     label=[
                                         Literal(
                                             f"{pLabel} in de rol van kind",
                                             lang='nl')
                                     ])

                for r in p.relations:
                    if e := getattr(r, 'event'):

                        relationTypeName = r.RelationType.lower().replace(
                            'other: ', '').title().replace(' ', '')

                        # Switch to ontology graph
                        g = rdfSubject.db = ontologyGraph
                        RoleClass = type(
                            r.RelationType, (Role, ),
                            {"rdf_type": roar.term(relationTypeName)})

                        rType = RoleType(roar.term(relationTypeName),
                                         subClassOf=roar.Role,
                                         label=[relationTypeName])

                        # Switch to A2A graph
                        g = rdfSubject.db = graph
                        eUri = deed.term(d.source.guid + '?event=' + e.id)
                        role = RoleClass(
                            None,
                            carriedIn=eUri,
                            carriedBy=[person],
                            label=[
                                Literal(
                                    f"{pLabel} in de rol van {r.RelationType}",
                                    lang='nl')
                            ])

                persons.append(person)

            # locations and roles
            locations = []
            try:

                if locationremarks := d.source.Remarks['Opmerking'][
                        'Locatieomschrijving']:

                    if type(locationremarks) == str:
                        locationremarks = [locationremarks]

                    for n, locName in enumerate(locationremarks, 1):
                        uri = deed.term(d.source.guid + '?location=' + str(n))
                        location = Location(uri, label=[locName])  # notarieel

                        locationRole = LocationRole(
                            None,
                            carriedIn=event,
                            carriedBy=[location],
                            label=[
                                Literal(
                                    f"{locName} in de rol van Locatieomschrijving",
                                    lang='nl')
                            ])

                        locations.append(location)
            except:
                pass

            # temp connection
            sourceIndex.event = events
            sourceIndex.person = persons
            sourceIndex.scan = scans
            sourceIndex.location = locations

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

    graph = bindNS(graph)
    graph.serialize(path, format='trig')

    return ontologyGraph, thesaurusGraph


if __name__ == "__main__":
    main()
