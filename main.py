"""

Additional packages needed:

- RDFAlchemy: 
- pya2a: pip install git+https://github.com/LvanWissen/pya2a.git

"""

import multiprocessing

import os
import json
import gzip
import uuid
import unidecode
from collections import defaultdict

from eadParser import parseEAD
from pya2a import DocumentCollection as A2ADocumentCollection

from rdflib import Dataset, Namespace, Literal, BNode, XSD, RDF, RDFS, URIRef
from rdfalchemy import rdfSubject

import rdflib.graph
from rdflib.term import skolem_genid
from model import *

ga = Namespace("https://data.goldenagents.org/datasets/")
rdflib.graph.DATASET_DEFAULT_GRAPH_ID = ga

gaPersonName = Namespace("https://data.goldenagents.org/datasets/personname/")

index2name = {
    "08953f2f-309c-baf9-e5b1-0cefe3891b37": "SAA-ID-001_SAA_Index_op_notarieel_archief",
    "f6e5401f-c486-5f3d-6a5c-6e277e12628e": "SAA-ID-002_SAA_Index_op_doopregisters",
    "2f352e18-256e-b4d1-e74f-3ffaf5e633f1": "SAA-ID-003_SAA_Index_op_ondertrouwregisters",
    "47828428-360d-afdd-1f07-2c13e34635e1": "SAA-ID-004_SAA_Index_op_kwijtscheldingen",
    "23d6fddb-4839-f080-2b0a-05a21c6162e8": "SAA-ID-005_SAA_Index_op_poorterboeken",
    "c53f836b-d7f0-fcd0-fc99-09192ccb17ad": "SAA-ID-006_SAA_Index_op_confessieboeken",
    "d46628d6-2ed4-95a0-cafc-4cdbb4174263": "SAA-ID-007_SAA_Index_op_boetes_op_trouwen_en_begraven",
    "9823b7a8-ab79-a098-4ab0-26e799ea5659": "SAA-ID-008_SAA_Index_op_begraafregisters_voor_1811",
    "8137be5e-1977-9c2b-1ead-b031fe39ed1e": "SAA-ID-009_SAA_Index_op_overledenen_gast_pest_werk_spinhuis",
    "760c1b75-122c-8965-170a-9b6701184533": "SAA-ID-010_SAA_Index_op_averijgrossen",
    "d5e8b387-d8f9-8a8b-dd17-00f7b6761553": "SAA-ID-011_SAA_Index_op_boedelpapieren",
    "3349cddf-c176-75e8-005f-705dbca96c4f": "SAA-ID-012_SAA_Index_op_lidmatenregister_doopsgezinde_gemeente",
}

index2nicename = {
    "08953f2f-309c-baf9-e5b1-0cefe3891b37": "Notariële Archieven 1578-1915",
    "f6e5401f-c486-5f3d-6a5c-6e277e12628e": "Doopregisters voor 1811",
    "2f352e18-256e-b4d1-e74f-3ffaf5e633f1": "Ondertrouwregisters 1565-1811",
    "47828428-360d-afdd-1f07-2c13e34635e1": "Kwijtscheldingen voor 1811",
    "23d6fddb-4839-f080-2b0a-05a21c6162e8": "Poorters 1531-1652",
    "c53f836b-d7f0-fcd0-fc99-09192ccb17ad": "Confessieboeken 1535-1732",
    "d46628d6-2ed4-95a0-cafc-4cdbb4174263": "Boetes op begraven",
    "9823b7a8-ab79-a098-4ab0-26e799ea5659": "Begraafregisters voor 1811",
    "8137be5e-1977-9c2b-1ead-b031fe39ed1e": "Overledenen Gast-, Pest-, Werk- en Spinhuis 1739-1812",
    "760c1b75-122c-8965-170a-9b6701184533": "Averijgrossen 1700-1810",
    "d5e8b387-d8f9-8a8b-dd17-00f7b6761553": "Boedelpapieren 1634-1938",
    "3349cddf-c176-75e8-005f-705dbca96c4f": "Lidmatenregister Doopsgezinde Gemeente",
}

name2index = {
    "SAA-ID-001_SAA_Index_op_notarieel_archief": "08953f2f-309c-baf9-e5b1-0cefe3891b37",
    "SAA-ID-002_SAA_Index_op_doopregisters": "f6e5401f-c486-5f3d-6a5c-6e277e12628e",
    "SAA-ID-003_SAA_Index_op_ondertrouwregisters": "2f352e18-256e-b4d1-e74f-3ffaf5e633f1",
    "SAA-ID-004_SAA_Index_op_kwijtscheldingen": "47828428-360d-afdd-1f07-2c13e34635e1",
    "SAA-ID-005_SAA_Index_op_poorterboeken": "23d6fddb-4839-f080-2b0a-05a21c6162e8",
    "SAA-ID-006_SAA_Index_op_confessieboeken": "c53f836b-d7f0-fcd0-fc99-09192ccb17ad",
    "SAA-ID-007_SAA_Index_op_boetes_op_trouwen_en_begraven": "d46628d6-2ed4-95a0-cafc-4cdbb4174263",
    "SAA-ID-008_SAA_Index_op_begraafregisters_voor_1811": "9823b7a8-ab79-a098-4ab0-26e799ea5659",
    "SAA-ID-009_SAA_Index_op_overledenen_gast_pest_werk_spinhuis": "8137be5e-1977-9c2b-1ead-b031fe39ed1e",
    "SAA-ID-010_SAA_Index_op_averijgrossen": "760c1b75-122c-8965-170a-9b6701184533",
    "SAA-ID-011_SAA_Index_op_boedelpapieren": "d5e8b387-d8f9-8a8b-dd17-00f7b6761553",
    "SAA-ID-012_SAA_Index_op_lidmatenregister_doopsgezinde_gemeente": "3349cddf-c176-75e8-005f-705dbca96c4f",
}

language2iso = {
    "nederlands": "nl",
    "engels": "en",
    "frans": "fr",
    "duits": "de",
    "spaans": "es",
    "italiaans": "it",
    "portugees": "pt",
    "deens": "da",
    "latijn": "la",
    "onbekend": "unknown",
    "zweeds": "sv",
    "overig": "other",
}

# Global dictionaries
identifier2book = defaultdict(dict)
identifier2physicalBook = defaultdict(dict)
collection2physicalCollection = dict()

with open("data/uri2notary.json") as infile:
    uri2notary = json.load(infile)

    uri2notary = {URIRef(k): [URIRef(i) for i in v] for k, v in uri2notary.items()}

with open("data/concordance/bg_mapping_index_guid.json") as infile:
    bg_guid2index = json.load(infile)

# with open('data/scanid2name_5075.json') as infile:
#     scanid2name = json.load(infile)

# with open('data/scanids/collection2scansuuid.json') as infile:
#     collection2scansuuid = json.load(infile)

# with open('data/scanids/collection2scansname.json') as infile:
#     collection2scansname = json.load(infile)

# Locations (Churches and Graveyards for Baptism and Burial)
with open("data/churches/label2location.json") as infile:
    labelChurch2location = json.load(infile)

with open("data/churches/label2religion.json") as infile:
    labelReligion2religion = json.load(infile)

with open("data/churches/churches.json") as infile:
    churchesDict = json.load(infile)
    churchesDict = {i["@id"]: i for i in churchesDict["@graph"]}

with open("data/churches/religions.json") as infile:
    religionsDict = json.load(infile)
    religionsDict = {i["@id"]: i for i in religionsDict["@graph"]}

# Functions
def unique(*args, sep="", ns=None):
    """Function to generate a unique BNode based on a series of arguments.

    Uses the uuid5 function to generate a uuid from one or multiple ordered
    arguments. This way, the BNode function of rdflib can be used, without the
    need to filter strange characters or spaces that will break the serialization.

    Returns:
        BNode: Blank node with identifier that is based on the function's input.
    """

    identifier = "".join(str(i) for i in args)  # order matters

    unique_id = uuid.uuid5(uuid.NAMESPACE_X500, identifier)

    if ns:
        return ns.term(str(unique_id))
    else:
        return BNode(unique_id)


def thesaurus(name, ClassType, defaultGraph, thesaurusGraph, subClassOf=None):

    if not name:
        return None, ""

    name = name.replace("other:", "").replace("Other:", "").strip()
    namenorm = unidecode.unidecode(name)
    namenorm = namenorm.title()
    namenorm = "".join(
        [i for i in namenorm if i.lower() in "abcdefghijklmnopqrstuvwxyz"]
    )

    if not namenorm:  # if no characters are left
        return None, ""

    g = rdfSubject.db = thesaurusGraph

    classType = ClassType(thes.term(namenorm), label=[name])

    if subClassOf:
        classType.subClassOf = subClassOf

    g = rdfSubject.db = defaultGraph  # restore graph

    return classType, name


def getEventPlace(placeName: str) -> Location:
    """
    Gives back an RDFAlchemy Location object based on the name of a church or graveyard.

    A mapping is used to map the right label (in source) to the right URI.

    Example Church data:
        ```json
        {
            "@id": "https://data.goldenagents.org/thesaurus/NieuweKerk",
            "@type": "Location",
            "label": "Nieuwe Kerk",
            "religions": ["https://data.goldenagents.org/thesaurus/Hervormd", "https://data.goldenagents.org/thesaurus/RoomsKatholiek"],
            "adamlink": "https://adamlink.nl/geo/building/nieuwe-kerk/1222",
            "wikidata": null
        }
        ```

    Args:
        placeName (str): The name of the church or graveyard, as indicated by the City Archives of Amsterdam.

    Returns:
        Location: ROAR Location instance
    """ """
    """

    locations = []
    churchesUris = labelChurch2location.get(placeName, [])

    for churchUri in churchesUris:

        churchData = churchesDict.get(churchUri, {})
        label = churchData["label"]
        religionUris = churchData["religions"]

        religions = []
        for religionUri in religionUris:

            religion = getReligion(religionUri=religionUri)
            religions.append(religion)

        sameAs = [
            URIRef(i) for i in [churchData["adamlink"], churchData["wikidata"]] if i
        ]

        eventPlace = Location(
            URIRef(churchUri), label=[label], hasReligion=religions, sameAs=sameAs
        )

        locations.append(eventPlace)

    return locations


def getReligion(religionName="", religionUri="") -> Concept:
    """
    Gives back an RDFAlchemy Concept object based on the name of a religion.

    A mapping is used in case a relgionName is supplied.

    Example Religion data:
        ```json
        {
            "@id": "https://data.goldenagents.org/thesaurus/Doopsgezind",
            "@type": "Concept",
            "label": "Doopsgezind"
        }
        ```

    Args:
        religionName (str, optional): Name of the religion as given in the source (SAA). Defaults to "".
        religionUri (str, optional): URI of the religion. Defaults to "".

    Returns:
        Concept: SKOS Concept instance
    """

    if religionName:
        religionUri = labelReligion2religion.get(religionName)
    elif not religionUri:
        return None

    religionData = religionsDict.get(religionUri)

    if not religionData:
        print(religionName, religionUri)
        return None

    religionLabel = religionData["label"]
    religion = Concept(URIRef(religionUri), label=[religionLabel])

    return religion


def parsePersonName(
    nameString=None, givenName=None, surnamePrefix=None, baseSurname=None
):
    """ """

    pns = []
    labels = []

    if (
        nameString
        and givenName is None
        and surnamePrefix is None
        and baseSurname is None
    ):

        if ", " in nameString:
            baseSurname, givenName = nameString.rsplit(", ", 1)

            if "[" in givenName:
                givenName, surnamePrefix = givenName.split("[", 1)

                givenName = givenName.strip()
                surnamePrefix = surnamePrefix[:-1]
            else:
                surnamePrefix = None
        else:
            givenName = None
            surnamePrefix = None
            baseSurname = nameString

    literalName = " ".join(i for i in [givenName, surnamePrefix, baseSurname] if i)

    # Attempt to limit the number of bNodes. Use our own uri.
    pn = PersonName(
        unique(givenName, surnamePrefix, baseSurname, sep="@ga@", ns=gaPersonName),
        literalName=literalName if literalName else "Unknown",
        label=literalName if literalName else "Unknown",
        givenName=givenName,
        surnamePrefix=surnamePrefix,
        baseSurname=baseSurname,
    )

    pns.append(pn)
    labels.append(pn.label)

    return pns, labels


def bindNS(g):

    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("rpp", rpp)
    g.bind("thes", thes)
    g.bind("pnv", pnv)
    g.bind("sem", sem)
    g.bind("dcterms", DCTERMS)
    g.bind("file", file)
    g.bind("foaf", FOAF)
    g.bind("oa", oa)
    g.bind("as", AS)
    g.bind("deed", deed)
    g.bind("skos", SKOS)
    g.bind("prov", PROV)

    return g


def skolemize(g):

    new_g = Graph(identifier=g.identifier)
    g = g.skolemize(new_graph=new_g, authority=ga, basepath=skolem_genid)

    return g


def main(
    eadfolder="data/ead",
    a2afolder="data/a2a",
    outfile="rpp.trig",
    splitFile=True,
    splitSize=100,
    temporal=False,
    window=10,
    shift=5,
):

    ds = Dataset()

    # EAD
    print("EAD parsing!")
    g = rdfSubject.db = ds.graph(identifier=ga.term("saa/ead/"))
    for dirpath, dirname, filenames in os.walk(eadfolder):
        for n, f in enumerate(sorted(filenames), 1):
            print(f"{n}/{len(filenames)} {f}")
            if f.endswith(".xml"):
                convertEAD(os.path.join(dirpath, f), g)
            else:
                continue

            if splitFile:
                path = f"trig/{f}.trig"
                g = skolemize(g)
                g = bindNS(g)

                print("Serializing to", path)
                g.serialize(path, format="trig")  # TEMPORARY
                ds.remove_graph(g)
                g = rdfSubject.db = ds.graph(identifier=ga.term("saa/ead/"))
            else:
                pass  # nobody wants a single file

    # with open('data/concordance/5001_identifier2physicalBook.json',
    #           'w') as outfile:
    #     json.dump(identifier2physicalBook, outfile)

    # with open('data/concordance/5001_identifier2book.json', 'w') as outfile:
    #     json.dump(identifier2book, outfile)

    # A2A
    print("A2A parsing!")
    g = rdfSubject.db = ds.graph(identifier=ga.term("saa/a2a/"))
    for dirpath, dirname, filenames in os.walk(a2afolder):

        if dirpath == "data/a2a":  # one level deeper
            continue

        # # DTB + NA + Confessie
        # if 'doop' not in dirpath and 'ondertr' not in dirpath and 'begraaf' not in dirpath:
        #     continue

        # if "nota" not in dirpath:
        #     continue

        # DTB + NA for now
        # if 'begraafreg' not in dirpath and 'ondertrouwregisters' not in dirpath and 'doopregisters' not in dirpath and 'nota' not in dirpath:
        #    continue

        filenames = [
            os.path.abspath(os.path.join(dirpath, i))
            for i in sorted(filenames)
            if i.endswith(".xml")
        ]

        colName = dirpath.rsplit("/", 1)[-1]
        indexCollectionURI = a2a.term(name2index[colName])
        indexCollectionName = "Index collection: " + index2nicename[name2index[colName]]

        chunks = []
        foldername = dirpath.rsplit("/")[-1]

        if temporal:
            temporals = []

            years = range(temporal[0], temporal[1] + 1, shift)
            for year in years:
                beginRestriction = year

                end = year + window

                if end <= temporal[1]:
                    endRestriction = end
                elif temporal[1] - end > shift:
                    endRestriction = temporal[1]
                else:
                    continue

                temporals.append((beginRestriction, endRestriction))
        else:
            temporals = [False]

        for temp in temporals:
            nSplit = 0
            fns = []

            for n, f in enumerate(filenames, 1):
                fns.append(f)

                if n % splitSize == 0 or n == len(filenames):
                    nSplit += 1
                    path = f"trig/{foldername}_{str(nSplit).zfill(4)}.trig"
                    chunks.append(
                        (fns, path, indexCollectionURI, indexCollectionName, temp)
                    )
                    fns = []

                    # # TEMP BREAK
                    # break

        with multiprocessing.Pool(
            processes=max(multiprocessing.cpu_count() - 1, 1)
        ) as pool:

            graphs = pool.starmap(convertA2A, chunks)

        for og, tg in graphs:
            ontologyGraph = ds.graph(identifier=rpp)
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
    # print("HTR parsing!")
    # g = rdfSubject.db = ds.graph(identifier=ga.term('saa/htr/'))
    # TODO

    ## Finished!

    ds = bindNS(ds)

    if not splitFile:
        print(f"Serializing to {outfile}")
        ds.serialize("trig/rpp.trig", format="trig")
    else:
        # ontology
        g = rdfSubject.db = ds.graph(identifier=rpp)
        g.serialize("trig/rpp.trig", format="trig")

        # thesaurus
        g = rdfSubject.db = ds.graph(identifier=thes)
        g.serialize("trig/thesaurus.trig", format="trig")


def convertEAD(xmlfile, g):

    eadDocument = parseEAD(xmlfile)

    c = eadDocument.collection[0]

    uri = URIRef(f"https://archief.amsterdam/inventarissen/file/{c.id}")
    physicalUri = ead.term(c.id)

    # top collection, create a physical collection
    getCollection(c, uri, physicalUri=physicalUri)


def cToRdf(c, parent=None, collectionNumber=None, scanNamespace=None):

    uri = URIRef(f"https://archief.amsterdam/inventarissen/file/{c.id}")

    if c.level == "file":
        # Then this is a book --> InventoryBook

        if c.name:
            label = [Literal(c.name, lang="nl")]
        else:
            label = [Literal(f"Inventaris {c.identifier}", lang="nl")]

        bookIndex = BookIndex(
            uri,
            label=label,
            description=[c.description] if c.description else [],
            identifier=c.identifier,
            temporal=c.date.get("temporal"),
        )

        physicalBook = InventoryBook(
            ead.term(c.id),
            createdBy=uri2notary.get(uri, []),
            createdAt=TimeInterval(None, start=None, end=None),
        )

        bookIndex.indexOf = physicalBook

        creationEvent = DocumentCreation(
            ead.term(f"{c.id}#creation"),
            hasInput=[],
            hasOutput=[physicalBook],
            hasTimeStamp=c.date.get("hasTimeStamp"),
            hasBeginTimeStamp=c.date.get("hasBeginTimeStamp"),
            hasEndTimeStamp=c.date.get("hasEndTimeStamp"),
            hasEarliestBeginTimeStamp=c.date.get("hasEarliestBeginTimeStamp"),
            hasLatestBeginTimeStamp=c.date.get("hasLatestBeginTimeStamp"),
            hasEarliestEndTimeStamp=c.date.get("hasEarliestEndTimeStamp"),
            hasLatestEndTimeStamp=c.date.get("hasLatestEndTimeStamp"),
        )

        if notaryUris := uri2notary.get(uri, []):
            for notaryUri in notaryUris:
                notaryRole = NotaryRole(
                    None, carriedIn=creationEvent, carriedBy=[notaryUri]
                )

                Agent(notaryUri).participatesIn = [creationEvent]

        creationIndexEvent = DocumentCreation(
            ead.term(f"{c.id}#indexCreation"),
            hasInput=[physicalBook],
            hasOutput=[bookIndex],
        )

        return bookIndex, physicalBook, "file"

    else:
        # Not yet reached the end of the tree
        if parent and parent.resUri != URIRef(
            "https://archief.amsterdam/inventarissen/file/d5b98b7afa50a3af4fba8053b06fb961"
        ):  # these ids in the middle are not unique
            uri = None

        collection = getCollection(c, uri)

        return collection, None, "collection"


def getCollection(c, uri, physicalUri=None):

    collection = IndexCollection(
        uri,
        label=[c.name] if c.name else [c.identifier],
        description=[c.description] if c.description else [],
        identifier=c.identifier,
        temporal=c.date.get("temporal"),
    )

    collection2physicalCollection[c.identifier] = physicalUri

    if hasattr(c, "language"):
        language = [c.language]
        collection.language = language  # find dcterm alternative + iso
    else:
        language = []

    repositories = []
    authorities = []
    if hasattr(c, "repository"):
        if type(c.repository) != list:
            repository = [c.repository]
        else:
            repository = c.repository

        for i in repository:
            if "corpname" in c.repository:
                name = c.repository["corpname"]
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
    if hasattr(c, "origination"):
        if type(c.origination) != list:
            origination = [c.origination]
        else:
            origination = c.origination

        for i in origination:
            if "corpname" in i:
                name = i["corpname"]
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

    groupingCriteria = getGroupingCriteria(
        sourceType=[rpp.Inventory],
        sourceDate=c.date,
        sourceAuthor=originations,
        sourceLanguage=language,
    )
    collection.hasGroupingCriteria = groupingCriteria

    subcollections = []
    parts = []
    for ch in c.children:
        chIndex, chPhysical, chtype = cToRdf(ch, parent=collection)

        if chtype == "collection":
            subcollections.append(chIndex)
            chIndex.subCollectionOf = collection
        elif chtype == "file":
            parts.append(chIndex)
            chIndex.memberOf = collection

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

    creationEvent = CollectionCreation(None, hasInput=allUris, hasOutput=[collection])

    archiverRole = ArchiverAndCreatorRole(
        None, carriedIn=creationEvent, carriedBy=repositories
    )

    archivalDocumentRole = ArchivalDocumentRole(
        None, carriedIn=creationEvent, carriedBy=[collection]
    )

    if physicalUri:
        physicalCollection = InventoryCollection(physicalUri, hasMember=allUrisPhysical)
        collection.indexOf = physicalCollection

        return collection, physicalCollection
    else:
        return collection


def getAllChildren(c, ns):

    uris = []
    identifiers = []
    for child in c.children:
        if child.level == "file":
            uris.append(ns.term(child.id))
            identifiers.append(child.identifier)
        else:
            urisNew, identifiersNew = getAllChildren(child, ns=ns)
            uris += urisNew
            identifiers += identifiersNew

    return uris, identifiers


def getParentIdentifier(c):

    if hasattr(c, "parent"):
        identifier = getParentIdentifier(c.parent)
    else:
        identifier = c.identifier
    return identifier


def getGroupingCriteria(
    sourceType=[], sourceDate=dict(), sourceAuthor=[], sourceLanguage=None
):

    criteria = []

    if sourceType:
        criterion = GroupingCriterion(
            None, hasFilter=rpp.sourceType, hasFilterValue=sourceType
        )
        criteria.append(criterion)

    if sourceDate:

        start = sourceDate.get("hasEarliestBeginTimeStamp")
        end = sourceDate.get("hasLatestEndTimeStamp")

        criterion = GroupingCriterion(
            None, hasFilter=rpp.createdAt, hasFilterStart=start, hasFilterEnd=end
        )
        criteria.append(criterion)

    if sourceAuthor:
        criterion = GroupingCriterion(
            None, hasFilter=rpp.createdBy, hasFilterValue=sourceAuthor
        )
        criteria.append(criterion)

    if sourceLanguage:  # iso code?
        criterion = GroupingCriterion(
            None, hasFilter=rpp.language, hasFilterValue=sourceLanguage
        )
        criteria.append(criterion)

    return criteria


def convertA2A(
    filenames, path, indexCollectionURI, indexCollectionName, temporal=False, gz=True
):

    ontologyGraph = Graph(identifier=rpp)
    thesaurusGraph = Graph(identifier=thes)
    graph = Graph(identifier=a2a)

    if temporal:
        beginRestriction, endRestriction = temporal

        path = path.replace(".trig", f"_{beginRestriction}-{endRestriction}.trig")

    else:
        beginRestriction, endRestriction = None, None
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

    allIndexDocuments = []
    for xmlfile in filenames:

        c = A2ADocumentCollection(xmlfile)

        for d in c:

            cancelled = None

            if hasattr(d.source, "SourceDate"):
                registrationDate = d.source.SourceDate.date
            else:
                registrationDate = None

            # TEMPORAL RESTRICTION
            if beginRestriction and endRestriction:
                if registrationDate is None or type(registrationDate) == str:
                    continue
                elif (
                    registrationDate.year < beginRestriction
                    or registrationDate.year >= endRestriction
                ):
                    continue
            # TEMPORAL RESTRICTION

            collection = d.source.SourceReference.Archive
            inventory = d.source.SourceReference.RegistryNumber
            if hasattr(d.source.SourceReference, "Folio"):
                folio = d.source.SourceReference.Folio
            else:
                folio = None
            partOfUri = identifier2physicalBook[collection].get(
                inventory, URIRef("https://data.goldenagents.org/NOTHINGFOUNDHERE")
            )
            partOfIndexUri = identifier2book[collection].get(
                inventory, URIRef("https://data.goldenagents.org/NOTHINGFOUNDHERE")
            )
            # partOfUri = identifier2physicalBook[collection][inventory]
            # partOfIndexUri = identifier2book[collection][inventory]
            physicalCollectionUri = collection2physicalCollection[collection]

            createdByUris = []
            if creators := uri2notary.get(
                partOfIndexUri
            ):  # specifically for collection 5075
                for n in creators:
                    createdByUris.append(Agent(n))

            if hasattr(d.source, "SourcePlace"):
                name = d.source.SourcePlace.Place
                registrationPlace, registrationPlaceName = thesaurus(
                    name, Place, graph, thesaurusGraph
                )
            else:
                registrationPlace = None

            # source remarks
            comments = []
            try:
                if comment := d.source.Remarks["Opmerking"]["Opmerking"]:

                    comments.append(Literal(comment, lang="nl"))  # otr

                    if "Ondertrouwregister" in d.source.SourceType:
                        if "doorgehaald" in comment:
                            cancelled = True
                        else:
                            cancelled = False
            except:
                pass

            try:
                if comment := d.source.Remarks["Opmerking"]["Onderwerpsomschrijving"]:

                    comments.append(Literal(comment, lang="nl"))  # Notarieel
            except:
                pass

            inLanguage = None
            try:
                if language := d.source.Remarks["Opmerking"]["Taal"]:
                    isoLang = language2iso.get(language)
                    inLanguage = Literal(isoLang)  # Notarieel
            except:
                pass

            # source

            sourceTypeName = (
                d.source.SourceType.lower().replace("other:", "").title().strip()
            )

            # Switch to ontology graph
            g = rdfSubject.db = ontologyGraph

            sType, sTypeName = thesaurus(
                d.source.SourceType,
                DocumentType,
                graph,
                ontologyGraph,
                subClassOf=rpp.Document,
            )

            SourceClass = type(
                d.source.SourceType, (Document,), {"rdf_type": sType.resUri}
            )
            # sType = DocumentType(rpp.term(sourceTypeName),
            #                      subClassOf=rpp.Document,
            #                      label=[sourceTypeName])

            # Switch to A2A graph
            g = rdfSubject.db = graph

            # Part of which index?
            physicalCollection = InventoryCollection(physicalCollectionUri)
            indexCollection = IndexCollection(
                indexCollectionURI,
                label=[indexCollectionName],
                indexOf=physicalCollection,
            )

            # Physical deed
            physicalUri = partOfUri + "#" + d.source.guid
            physicalDocument = SourceClass(
                physicalUri,
                label=[Literal(f"Akte: {sourceTypeName}", lang="nl")],
                partOf=partOfUri,
                createdBy=createdByUris,
                createdAt=registrationDate,
                createdIn=registrationPlace,
            )

            # Index document
            indexUri = deed.term(d.source.guid)
            sourceIndex = IndexDocument(
                indexUri,
                label=[Literal(f"Index: {sourceTypeName}", lang="nl")],
                description=comments,
                inLanguage=inLanguage,
                cancelled=cancelled,
                indexOf=physicalDocument,
                memberOf=indexCollection,
            )

            allIndexDocuments.append(sourceIndex)

            ## scans
            scans = []
            scanCollectionURI = partOfUri + "/scans/"
            scanCollection = ScanCollection(scanCollectionURI)
            g.add((partOfUri, rpp.hasDigitalRepresentation, scanCollectionURI))

            scanNames = d.source.Remarks["filename"]

            for scanName, scan in zip(scanNames, d.source.scans):

                identifier = scan.Uri.rsplit("/")[-1].replace(".jpg", "")
                scanUri = partOfUri + "/scans/" + scanName

                s = Scan(
                    scanUri,
                    identifier=identifier,
                    label=[scanName],
                    memberOf=scanCollection,
                    depiction=[URIRef(scan.Uri)],
                )
                scans.append(s)

            scanCollection.hasMember = scans
            physicalDocument.hasScan = scans

            sourceIndex.onScan = scans
            sourceIndex.onPage = folio

            # events
            events = []
            for e in d.events:

                if "Confessieboeken" in sourceTypeName:
                    eventTypeName = "Confessie"
                else:
                    eventTypeName = (
                        e.EventType.lower()
                        .replace("other:", "")
                        .title()
                        .replace(" ", "")
                    )

                # Switch to ontology graph
                g = rdfSubject.db = ontologyGraph

                eType, eTypeName = thesaurus(
                    e.EventType,
                    EventType,
                    graph,
                    ontologyGraph,
                    subClassOf=rpp.RegistrationEvent,
                )

                RegistrationEventClass = type(
                    e.EventType, (RegistrationEvent,), {"rdf_type": eType.resUri}
                )

                # if eTypeName in ['Begraven', 'Doop', 'Overlijden']

                # EventClass = type(e.EventType, (Event, ),
                #                   {"rdf_type": eType.resUri})

                # eType = EventType(rpp.term(eventTypeName),
                #                   subClassOf=rpp.Event,
                #                   label=[eventTypeName])

                # Switch to A2A graph
                g = rdfSubject.db = graph

                # if d.source.EventDate and d.source.EventDate.date:
                #     sourceDate = d.source.EventDate.date
                # else:
                #     sourceDate = None  ## given in registrationDate

                if e.EventDate and e.EventDate.date:
                    eventDate = e.EventDate.date
                else:
                    eventDate = None

                # eventPlace for begraaf + doop
                if eventTypeName == "Begraven":
                    if type(d.source.Remarks["Opmerking"]) != str:
                        eventPlaceName = d.source.Remarks["Opmerking"].get(
                            "Begraafplaats"
                        )
                        eventPlaces = getEventPlace(eventPlaceName)
                    else:
                        eventPlaces = []

                elif eventTypeName == "Doop":
                    if type(d.source.Remarks["Opmerking"]) != str:
                        eventPlaceName = d.source.Remarks["Opmerking"].get("Kerk")
                        eventPlaces = getEventPlace(eventPlaceName)
                    else:
                        eventPlaces = []

                else:
                    eventPlaces = []

                # religion
                eventReligions = []
                if hasattr(e, "EventReligion"):
                    eventReligion = getReligion(religionName=e.EventReligion)
                    if eventReligion:
                        eventReligions.append(eventReligion)
                    else:
                        eventReligions = []

                # date
                if type(registrationDate) == str and len(registrationDate) == 4:
                    registrationDateLiteral = Literal(
                        registrationDate, datatype=XSD.gYear
                    )
                elif type(registrationDate) == str and len(registrationDate) == 7:
                    registrationDateLiteral = Literal(
                        registrationDate, datatype=XSD.gYearMonth
                    )
                elif registrationDate:
                    registrationDateLiteral = Literal(
                        registrationDate, datatype=XSD.date
                    )
                else:
                    registrationDateLiteral = None

                registrationEvent = RegistrationEventClass(
                    deed.term(d.source.guid + "?event=" + e.id),
                    hasPlace=[registrationPlace],
                    hasTimeStamp=registrationDateLiteral,
                    hasOutput=[physicalDocument],
                    label=[
                        Literal(
                            f"Registratie: {eventTypeName} ({registrationDate if registrationDate else '?'})",
                            lang="nl",
                        )
                    ],
                )
                events.append(registrationEvent)

                if type(eventDate) == str and len(eventDate) == 4:
                    eventDateLiteral = Literal(eventDate, datatype=XSD.gYear)
                elif type(eventDate) == str and len(eventDate) == 7:
                    eventDateLiteral = Literal(eventDate, datatype=XSD.gYearMonth)
                elif eventDate:
                    eventDateLiteral = Literal(eventDate, datatype=XSD.date)
                else:
                    eventDateLiteral = None

                # TODO
                # Which registrationEvents registers another event?
                # - Doop
                # - Begraafregisters
                # - ?

                # For now, do it for every event
                # if "Dopen" in d.source.SourceType or "Begraven" in d.source.SourceType:
                eventUri = a2a.term(
                    d.source.guid + "#" + "event"
                )  # Use our own NS for event that is registered?
                event = Event(
                    eventUri,
                    hasTimeStamp=eventDateLiteral,
                    hasPlace=eventPlaces,
                    hasReligion=eventReligions,
                    label=[
                        Literal(
                            f"{eventTypeName} ({eventDate if eventDate else '?'})",
                            lang="nl",
                        )
                    ],
                )

                registrationEvent.registers = event

            # persons and roles
            persons = []
            roles = []
            guid_roles = defaultdict(list)
            for n, p in enumerate(d.persons, 1):

                pEvents = [registrationEvent]

                personnames, pLabels = parsePersonName(
                    givenName=p.PersonName.PersonNameFirstName,
                    surnamePrefix=p.PersonName.PersonNamePrefixLastName,
                    baseSurname=p.PersonName.PersonNameLastName,
                )

                ## Annotation PersonName on scan (Notarial)

                if hasattr(p, "Remarks"):
                    if scanData := p.Remarks.get("diversen"):

                        if "Positie op scan" in scanData:

                            scanName = scanData["Positie op scan"]["scan"].upper()
                            scanPosition = scanData["Positie op scan"]["positie"]
                            coordinates = scanPosition.replace(" ", "")

                            # scanIdentifier = collection2scansname[collection][
                            #     scanName]
                            scanUri = partOfUri + "/scans/" + scanName

                            an = Annotation(
                                None,
                                hasBody=personnames[0],
                                hasTarget=SpecificResource(
                                    None,
                                    hasSource=scanUri,
                                    hasSelector=FragmentSelector(
                                        None,
                                        conformsTo=URIRef(
                                            "http://www.w3.org/TR/media-frags/"
                                        ),
                                        value=coordinates,
                                    ),
                                ),
                                # depiction=depiction,
                                label=pLabels,
                            )

                        if "Beroep" in scanData:

                            occupation, occupationName = thesaurus(
                                scanData["Beroep"],
                                OccupationObservation,
                                graph,
                                thesaurusGraph,
                            )

                            occupationRole = OccupationRole(
                                None,
                                carriedIn=registrationEvent,
                                carriedBy=[occupation],
                                label=[
                                    Literal(
                                        f"{occupationName} in de rol van beroepsomschrijving",
                                        lang="nl",
                                    )
                                ],
                            )

                            roles.append(occupationRole)

                        if "Plaats in bron" in scanData:

                            origin, originName = thesaurus(
                                scanData["Plaats in bron"], Place, graph, thesaurusGraph
                            )

                            originRole = OriginRole(
                                None,
                                carriedIn=registrationEvent,
                                carriedBy=[origin],
                                label=[
                                    Literal(
                                        f"{originName} in de rol van herkomstomschrijving",
                                        lang="nl",
                                    )
                                ],
                            )

                            roles.append(originRole)

                        if "Eerdere man" in scanData:

                            earlierHusbandName = scanData["Eerdere man"]

                            pnsEarlierHusband, labelsEarlierHusband = parsePersonName(
                                earlierHusbandName
                            )

                            earlierHusband = Person(
                                deed.term(d.source.guid + "?person=" + "EerdereMan"),
                                participatesIn=[registrationEvent],
                                hasName=pnsEarlierHusband,
                                label=[labelsEarlierHusband[0]],
                            )

                            role = EarlierHusband(
                                None,
                                carriedIn=registrationEvent,
                                carriedBy=[earlierHusband],
                                label=[
                                    Literal(
                                        f"{labelsEarlierHusband[0]} in de rol van eerdere man",
                                        lang="nl",
                                    )
                                ],
                            )

                            persons.append(earlierHusband)
                            roles.append(role)

                        if "Eerdere vrouw" in scanData:

                            earlierWifeName = scanData["Eerdere vrouw"]

                            pnsEarlierWife, labelsEarlierWife = parsePersonName(
                                earlierWifeName
                            )

                            earlierWife = Person(
                                deed.term(d.source.guid + "?person=" + "EerdereVrouw"),
                                participatesIn=[registrationEvent],
                                hasName=pnsEarlierWife,
                                label=[labelsEarlierWife[0]],
                            )

                            role = EarlierWife(
                                None,
                                carriedIn=registrationEvent,
                                carriedBy=[earlierWife],
                                label=[
                                    Literal(
                                        f"{labelsEarlierWife[0]} in de rol van eerdere vrouw",
                                        lang="nl",
                                    )
                                ],
                            )

                            persons.append(earlierWife)
                            roles.append(role)

                        if "Naamsvariant" in scanData:

                            nameVariant = scanData["Naamsvariant"]

                            pnVariants, _ = parsePersonName(nameVariant)
                            personnames += pnVariants

                        if "Overige namen" in scanData:

                            for otherName in scanData["Overige namen"]:
                                pass  # TODO

                ##
                pid = p.id.replace("Person:", "")
                person = Person(
                    deed.term(d.source.guid + "?person=" + pid),
                    hasName=personnames,
                    label=pLabels,
                )

                # birth in A2A defined
                if bd := getattr(p, "BirthDate"):

                    birthDate = bd.date
                    birthLabel = [
                        Literal(
                            f"Geboorte van {pLabels[0]} ({birthDate.isoformat() if birthDate else '?'})"
                        )
                    ]

                    birthEvent = Geboorte(
                        deed.term(d.source.guid + "?event=birth"),
                        hasTimeStamp=birthDate,
                        label=birthLabel,
                    )

                    role = ChildRole(
                        None,
                        carriedIn=birthEvent,
                        carriedBy=[person],
                        label=[Literal(f"{pLabels[0]} in de rol van Kind", lang="nl")],
                    )

                    pEvents.append(birthEvent)
                    roles.append(role)

                for r in p.relations:
                    if e := getattr(r, "event"):

                        # relationTypeName = r.RelationType.lower().replace(
                        #     'other:', '').title().replace(' ', '')

                        # Switch to ontology graph
                        # g = rdfSubject.db = ontologyGraph

                        # Catch for Confessieboeken that only have 'Verdachte' as role
                        if "Confessieboeken" in sourceTypeName:
                            relationType = "Verdachte"
                        else:
                            relationType = r.RelationType

                        rType, rTypeName = thesaurus(
                            relationType,
                            RoleType,
                            graph,
                            ontologyGraph,
                            subClassOf=rpp.Role,
                        )

                        RoleClass = type(
                            relationType, (Role,), {"rdf_type": rType.resUri}
                        )

                        # rType = RoleType(rpp.term(relationTypeName),
                        #                  subClassOf=rpp.Role,
                        #                  label=[relationTypeName])

                        # Switch to A2A graph
                        # g = rdfSubject.db = graph
                        eUri = deed.term(d.source.guid + "?event=" + e.id)
                        role = RoleClass(
                            None,
                            carriedIn=eUri,
                            carriedBy=[person],
                            label=[
                                Literal(
                                    f"{pLabels[0]} in de rol van {rTypeName}", lang="nl"
                                )
                            ],
                        )
                        guid_roles[pid].append(role)
                        roles.append(role)

                person.participatesIn = pEvents
                persons.append(person)

            # locations and roles
            locations = []
            if d.source.Remarks["Opmerking"]:
                if locationremarks := d.source.Remarks["Opmerking"][
                    "Locatieomschrijving"
                ]:

                    if type(locationremarks) == str:
                        locationremarks = [locationremarks]

                    for n, locName in enumerate(locationremarks, 1):
                        uri = deed.term(
                            d.source.guid + "?location=" + "Location" + str(n)
                        )
                        location = LocationObservation(
                            uri, label=[locName]
                        )  # notarieel

                        locationRole = LocationRole(
                            None,
                            carriedIn=registrationEvent,
                            carriedBy=[location],
                            label=[
                                Literal(
                                    f"{locName} in de rol van locatieomschrijving",
                                    lang="nl",
                                )
                            ],
                        )

                        locations.append(location)
                        roles.append(locationRole)

            # relations and roles
            relations = []
            if d.source.Remarks["Opmerking"]:
                if relatieinformatie := d.source.Remarks["Opmerking"][
                    "Relatie informatie"
                ]:

                    r1, r2 = None, None

                    uri = deed.term(d.source.guid + "?relation=" + "Relation1")
                    relation = Relation(uri, label=[relatieinformatie])

                    for pid, pRoles in guid_roles.items():
                        if len(pRoles) == 1:
                            role = pRoles[0]
                        else:
                            print("More than 1 or no role for this person!")
                            continue

                        if bg_guid2index.get(pid) == 1:
                            r1 = role
                            role.position = 1
                        elif bg_guid2index.get(pid) == 2:
                            r2 = role
                            role.position = 2
                        else:
                            # If there is only one person, but still a relation info
                            r2 = role
                            role.position = 1

                    # Relation in SAA is from p1 to p2 (p1 is husband of p2)
                    # We do it the other way round: p2 has husband p1
                    # Relations are bound to the person role

                    if r1:
                        pLabel = r1.carriedBy[0].hasName[0].literalName
                    else:
                        pLabel = "Onbekend"

                    relationRole = RelationRole(
                        None,
                        carriedIn=registrationEvent,
                        carriedBy=[relation],
                        relatedTo=r1,
                        label=[Literal(f"{relatieinformatie} ({pLabel})", lang="nl")],
                    )

                    if r2:
                        r2.hasRelation = [relationRole]

                    relations.append(relation)

            # Confessieboeken 'Overige namen'
            if d.source.Remarks["Opmerking"]:
                if otherNames := d.source.Remarks["Opmerking"]["Overige namen"]:

                    # If there is only one
                    if type(otherNames) == str:
                        otherNames = [otherNames]

                    for n, otherPersonName in enumerate(otherNames, 1):
                        uri = deed.term(
                            d.source.guid + "?otherName=" + "Location" + str(n)
                        )

                        pnsOtherPerson, labelsOtherPerson = parsePersonName(
                            otherPersonName
                        )

                        otherPerson = Person(
                            deed.term(d.source.guid + "?person=" + "Other" + str(n)),
                            participatesIn=[registrationEvent],
                            hasName=pnsOtherPerson,
                            label=[labelsOtherPerson[0]],
                        )

                        relationType = "Geregistreerde"
                        rType, rTypeName = thesaurus(
                            relationType,
                            RoleType,
                            graph,
                            ontologyGraph,
                            subClassOf=rpp.Role,
                        )

                        RoleClass = type(
                            relationType, (Role,), {"rdf_type": rType.resUri}
                        )

                        role = RoleClass(
                            None,
                            carriedIn=registrationEvent,
                            carriedBy=[otherPerson],
                            label=[
                                Literal(
                                    f"{labelsOtherPerson[0]} in de rol van {rTypeName}]",
                                    lang="nl",
                                )
                            ],
                        )

                        persons.append(otherPerson)
                        roles.append(role)

            sourceIndex.mentionsEvent = events
            sourceIndex.mentionsPerson = persons
            sourceIndex.mentionsLocation = locations
            sourceIndex.mentionsRelation = relations
            sourceIndex.mentionsRole = roles

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

    indexCollection.hasMember = allIndexDocuments

    graph = skolemize(graph)
    graph = bindNS(graph)

    # gzip
    if gz:
        with gzip.open(path + ".gz", "wb") as outfile:
            outfile.write(graph.serialize(format="trig").encode())
    else:
        graph.serialize(path, format="trig")

    return ontologyGraph, thesaurusGraph


if __name__ == "__main__":
    # main(temporal=(1620, 1670))
    main()
