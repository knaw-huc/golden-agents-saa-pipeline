import gzip
import os
import json

import unidecode

import multiprocessing

from rdflib import Graph
from main import skolemize, bindNS, parsePersonName, getEventPlace
from model import *

from lxml import etree as ET

gaIndexUri = Namespace(
    "https://data.goldenagents.org/datasets/begraafregisters_20190227/"
)
gaPersonName = Namespace("https://data.goldenagents.org/datasets/personname/")

with open("data/concordance/5001_identifier2physicalBook.json") as infile:
    identifier2physicalBook = json.load(infile)

with open("data/concordance/5001_identifier2book.json") as infile:
    identifier2book = json.load(infile)


# These classes are created dynamically in the main script
# by taking the values from the A2A.
class DTBBegraven(Document):
    rdf_type = URIRef("https://data.goldenagents.org/thesaurus/DtbBegraven")


class Begraven(RegistrationEvent):
    rdf_type = URIRef("https://data.goldenagents.org/thesaurus/Begraven")


class Geregistreerde(Role):
    rdf_type = URIRef("https://data.goldenagents.org/thesaurus/Geregistreerde")
    subClassOf = URIRef("https://data.goldenagents.org/thesaurus/Role")


def parse_xml(xml_file, gz=True):
    """
    Parse the old style XML data of the Amsterdam City Archives' Burial
    Registries in the new ROAR++ format. Writes every file to a TriG file.

    Args:
        xml_file (str): Path to the XML file to parse.
        gz (bool): Whether the TriG file should be gzipped.
    """

    print(f"Parsing {xml_file}")

    g = rdfSubject.db = Graph(identifier=gaIndexUri)

    tree = ET.parse(xml_file)
    records = tree.findall(".//indexRecord")

    for record in records:

        persons = []
        roles = []
        events = []
        locations = []
        scans = []

        identifier = record.attrib["id"]
        collection = record.find("toegangsnummer").text
        inventory = record.find("inventarisnummer").text

        bronverwijzing = (
            record.find("bronverwijzing").text
            if record.find("bronverwijzing") is not None
            else None
        )
        ingeschrevenen = record.findall("ingeschrevene")
        relatieinformatie = (
            record.find("relatieinformatie").text
            if record.find("relatieinformatie") is not None
            else None
        )
        urlScan = (
            record.find("urlScan").text if record.find("urlScan") is not None else None
        )

        eventDate = (
            record.find("datumBegrafenis").text
            if record.find("datumBegrafenis") is not None
            else None
        )

        if not eventDate:
            continue

        begraafplaats = (
            record.find("begraafplaats").text
            if record.find("begraafplaats") is not None
            else None
        )

        partOfUri = URIRef(
            identifier2physicalBook[collection].get(
                inventory, "https://data.goldenagents.org/NOTHINGFOUNDHERE"
            )
        )

        indexCollectionURI = gaIndexUri.term("index")
        indexCollection = IndexCollection(indexCollectionURI)

        scanCollectionURI = partOfUri + "/scans/"
        scanCollection = ScanCollection(scanCollectionURI)
        g.add((partOfUri, roar.hasDigitalRepresentation, scanCollectionURI))

        # Physical deed
        physicalUri = partOfUri + "#" + identifier
        physicalDocument = DTBBegraven(
            physicalUri,
            label=[Literal(f"Akte: DTB Begraven", lang="nl")],
            partOf=partOfUri,
        )

        # Index document
        sourceIndex = IndexDocument(
            gaIndexUri.term(identifier),
            label=[Literal(f"Index: DTB Begraven", lang="nl")],
            indexOf=physicalDocument,
            memberOf=indexCollection,
        )

        if begraafplaats:
            eventPlace = getEventPlace(begraafplaats)
        else:
            eventPlace = None

        eUri = gaIndexUri.term(identifier + "?event=" + "Event1")

        registrationDate = eventDate

        if len(registrationDate) == 4:
            registrationDateLiteral = Literal(registrationDate, datatype=XSD.gYear)
        elif len(registrationDate) == 7:
            registrationDateLiteral = Literal(registrationDate, datatype=XSD.gYearMonth)
        elif registrationDate:
            registrationDateLiteral = Literal(registrationDate, datatype=XSD.date)
        else:
            registrationDateLiteral = None

        registrationEvent = Begraven(
            eUri,
            # hasPlace=registrationPlace,
            hasTimeStamp=registrationDateLiteral,
            hasOutput=[physicalDocument],
            label=[
                Literal(
                    f"Registratie: DTB Begraven ({registrationDate if registrationDate else '?'})",
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

        eventUri = gaIndexUri.term(
            identifier + "#" + "event"
        )  # Use our own NS for event that is registered?
        event = Event(
            None,
            hasTimeStamp=eventDateLiteral,
            hasPlace=eventPlace,
            label=[
                Literal(f"DTB Begraven ({eventDate if eventDate else '?'})", lang="nl")
            ],
        )

        registrationEvent.registers = event

        for n, i in enumerate(ingeschrevenen, 1):
            pns, labels = parsePersonName(
                givenName=i.find("voornaam").text
                if i.find("voornaam") is not None
                else None,
                surnamePrefix=i.find("tussenvoegsel").text
                if i.find("tussenvoegsel") is not None
                else None,
                baseSurname=i.find("achternaam").text
                if i.find("achternaam") is not None
                else None,
            )

            pUri = gaIndexUri.term(identifier + "?person=" + str(n))
            p = Person(
                pUri, hasName=pns, label=labels, participatesIn=[registrationEvent]
            )
            persons.append(p)

            role = Geregistreerde(
                None,
                carriedIn=eUri,
                carriedBy=[p],
                position=n,
                label=[Literal(f"{labels[0]} in de rol van geregistreerde", lang="nl")],
            )

            roles.append(role)

        if urlScan:
            scanName = urlScan.replace(
                "https://archief.amsterdam/inventarissen/inventaris/5001.nl.html#", ""
            )
            scanName = scanName.upper()
            scanName.replace(".JPG", "")

            scanUri = partOfUri + "/scans/" + scanName

            s = Scan(scanUri, label=[scanName], memberOf=scanCollection)
            scans.append(s)

        scanCollection.hasMember = scans
        physicalDocument.hasScan = scans

        sourceIndex.onScan = scans
        sourceIndex.onPage = bronverwijzing

        # relations and roles
        relations = []

        if relatieinformatie:

            r1, r2 = None, None

            if len(roles) == 1:
                r1 = roles[0]
            elif len(roles) == 2:
                r1, r2 = roles

            uri = gaIndexUri.term(identifier + "?relation=" + "Relation1")
            relation = Relation(uri, label=[relatieinformatie])

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

        sourceIndex.mentionsEvent = events
        sourceIndex.mentionsPerson = persons
        sourceIndex.mentionsLocation = locations  # empty for this dataset
        sourceIndex.mentionsRelation = relations

    g = skolemize(g)
    g = bindNS(g)

    print("Serializing...")

    filename = os.path.split(xml_file)[1]
    filename = filename.replace(".xml", ".trig")
    path = f"trig/{filename}"

    # gzip
    if gz:
        with gzip.open(path + ".gz", "wb") as outfile:
            outfile.write(g.serialize(format="trig").encode())
    else:
        g.serialize(path, format="trig")


if __name__ == "__main__":

    folder = "data/begraafregisters/"

    xml_files = [
        os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".xml")
    ]

    with multiprocessing.Pool(processes=3) as pool:

        pool.map(parse_xml, xml_files)

    # parse_xml(
    #     "data/begraafregisters/SAA_Index_op_begraafregisters_voor_1811_DUBBELE__20190227_001.xml"
    # )

    print("Done!")
