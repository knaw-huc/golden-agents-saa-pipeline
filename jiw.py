import json

from main import thesaurus, bindNS
from model import *

jiw = Namespace("https://data.goldenagents.org/datasets/jaikwil/")


class Ondertrouwregister(Document):
    rdf_type = thes.Ondertrouwregister


def main(infile, path):

    with open(infile) as infile:
        data = json.load(infile)

    indexCollection = IndexCollection(
        URIRef("https://data.goldenagents.org/datasets/jaikwil/records/"))

    ontologyGraph = Graph(identifier=roar)
    thesaurusGraph = Graph(identifier=thes)
    graph = Graph(identifier=jiw)

    allIndexDocuments = []

    for n, d in enumerate(data, 1):

        if n % 100 == 0:
            print(f"{n}/{len(data)}", end='\r')

        # Switch to A2A graph
        g = rdfSubject.db = graph

        mentionedPersons = []
        mentionedLocations = []
        mentionedEvents = []

        mentionedOccupations = []
        mentionedRelations = []
        mentionedReligions = []

        # Physical deed
        physicalDocument = Ondertrouwregister(
            URIRef(d['indexOf']),
            label=[Literal(f"Akte: Ondertrouwregister", lang='nl')],
            partOf=URIRef(d['partOf']),
            createdAt=d['date'],
            createdIn=d['location'])

        # Index document
        sourceIndex = IndexDocument(
            URIRef(d['id']),
            label=[Literal(f"Index: Ondertrouwregister", lang='nl')],
            description=[d['comments']] if d['comments'] else [],
            indexOf=physicalDocument,
            memberOf=indexCollection)

        allIndexDocuments.append(sourceIndex)

        registrationEvent = URIRef(d['mentionsRegistrationEvent'])
        mentionedEvents.append(registrationEvent)

        pnGroom = PersonName(
            URIRef(d['groom']['id'] + '-pn'),
            givenName=d['groom']['hasName']['givenName'],
            surnamePrefix=d['groom']['hasName']['surnamePrefix'],
            baseSurname=d['groom']['hasName']['baseSurname'],
            literalName=d['groom']['hasName']['literalName'],
            label=d['groom']['hasName']['literalName'])

        groom = Person(URIRef(d['groom']['id']),
                       hasName=[pnGroom],
                       label=[pnGroom.label])

        groomRole = Bruidegom(
            URIRef(d['groom']['id'] + '-role'),
            age=d['groom']['age'],
            literate=d['groom']['signature'],
            carriedIn=registrationEvent,
            carriedBy=[groom],
            label=[
                Literal(f"{pnGroom.label} in de rol van Bruidegom", lang='nl')
            ])

        if d['groom']['origin']:
            locName = d['groom']['origin']
            location = Location(URIRef(d['groom']['id'] + '-origin'),
                                label=[locName])

            locationRole = OriginRole(
                URIRef(d['groom']['id'] + '-origin-role'),
                carriedIn=registrationEvent,
                carriedBy=[location],
                label=[Literal(f"{locName} (herkomst)", lang='nl')])

            groomRole.hasLocation = [locationRole]

            mentionedLocations.append(location)

        if d['groom']['homeLocation']:
            locName = d['groom']['homeLocation']
            location = Location(URIRef(d['groom']['id'] + '-address'),
                                label=[locName])

            locationRole = AddressRole(
                URIRef(d['groom']['id'] + '-address-role'),
                carriedIn=registrationEvent,
                carriedBy=[location],
                label=[Literal(f"{locName} (adres)", lang='nl')])

            groomRole.hasLocation = [locationRole]

            mentionedLocations.append(location)

        if d['groom']['occupation']:
            occName = d['groom']['occupation']
            occupation = Occupation(URIRef(d['groom']['id'] + '-occupation'),
                                    label=[occName])

            occupationRole = OccupationRole(
                URIRef(d['groom']['id'] + '-occupation-role'),
                carriedIn=registrationEvent,
                carriedBy=[occupation],
                label=[Literal(f"{occName} (beroep)", lang="nl")])

            groomRole.hasOccupation = [occupationRole]

            mentionedOccupations.append(occupation)

        if d['groom']['religion']:
            religionName = d['groom']['religion']
            religion = Religion(URIRef(d['groom']['id'] + '-religion'),
                                label=[religionName])

            religionRole = PersonReligionRole(
                URIRef(d['groom']['id'] + '-religion-role'),
                carriedIn=registrationEvent,
                carriedBy=[religion],
                label=[Literal(f"{religionName} (religie)", lang="nl")])

            groomRole.hasReligion = [religionRole]

            mentionedReligions.append(religion)

        mentionedPersons.append(groom)

        if d['groom']['exWife']:

            pnExWife = PersonName(
                URIRef(d['groom']['exWife']['id'] + '-pn'),
                givenName=d['groom']['exWife']['hasName']['givenName'],
                surnamePrefix=d['groom']['exWife']['hasName']['surnamePrefix'],
                baseSurname=d['groom']['exWife']['hasName']['baseSurname'],
                literalName=d['groom']['exWife']['hasName']['literalName'],
                label=d['groom']['exWife']['hasName']['literalName'])

            exWife = Person(URIRef(d['groom']['exWife']['id']),
                            hasName=[pnExWife],
                            label=[pnExWife.label])

            exWifeRole = EarlierWife(
                URIRef(d['groom']['exWife']['id'] + '-role'),
                carriedIn=registrationEvent,
                carriedBy=[exWife],
                label=[
                    Literal(f"{pnExWife.label} in de rol van Eerdere Vrouw",
                            lang='nl')
                ])

            mentionedPersons.append(exWife)

        for w in d['groom']['witnesses']:

            pnWitness = PersonName(URIRef(w['id'] + '-pn'),
                                   givenName=w['hasName']['givenName'],
                                   surnamePrefix=w['hasName']['surnamePrefix'],
                                   baseSurname=w['hasName']['baseSurname'],
                                   literalName=w['hasName']['literalName'],
                                   label=w['hasName']['literalName'])
            witness = Person(URIRef(w['id']),
                             hasName=[pnWitness],
                             label=[pnWitness.label])

            witnessRole = Getuige(
                URIRef(w['id'] + '-role'),
                carriedIn=registrationEvent,
                carriedBy=[witness],
                label=[
                    Literal(f"{pnWitness.label} in de rol van Getuige",
                            lang='nl')
                ])

            if w['relation']:

                relation = Relation(URIRef(w['id'] + '-relation'),
                                    label=[w['relation']])

                relationRole = RelationRole(
                    URIRef(w['id'] + '-relation-role'),
                    carriedIn=registrationEvent,
                    carriedBy=[relation],
                    relatedTo=witness,
                    label=[
                        Literal(f"{w['relation']} ({pnWitness.label})",
                                lang='nl')
                    ])

                groomRole.hasRelation = [relationRole]

                mentionedRelations.append(relation)

            mentionedPersons.append(witness)

        pnBride = PersonName(
            URIRef(d['bride']['id'] + '-pn'),
            givenName=d['bride']['hasName']['givenName'],
            surnamePrefix=d['bride']['hasName']['surnamePrefix'],
            baseSurname=d['bride']['hasName']['baseSurname'],
            literalName=d['bride']['hasName']['literalName'],
            label=d['bride']['hasName']['literalName'])

        bride = Person(URIRef(d['bride']['id']),
                       hasName=[pnBride],
                       label=[pnBride.label])

        brideRole = Bruid(
            URIRef(d['bride']['id'] + '-role'),
            age=d['bride']['age'],
            literate=d['bride']['signature'],
            carriedIn=registrationEvent,
            carriedBy=[bride],
            label=[Literal(f"{pnBride.label} in de rol van Bruid", lang='nl')])

        if d['bride']['origin']:
            locName = d['bride']['origin']
            location = Location(URIRef(d['bride']['id'] + '-origin'),
                                label=[locName])

            locationRole = OriginRole(
                URIRef(d['bride']['id'] + '-origin-role'),
                carriedIn=registrationEvent,
                carriedBy=[location],
                label=[Literal(f"{locName} (herkomst)", lang='nl')])

            brideRole.hasLocation = [locationRole]

            mentionedLocations.append(location)

        if d['bride']['homeLocation']:
            locName = d['bride']['homeLocation']
            location = Location(URIRef(d['bride']['id'] + '-address'),
                                label=[locName])

            locationRole = AddressRole(
                URIRef(d['bride']['id'] + '-address-role'),
                carriedIn=registrationEvent,
                carriedBy=[location],
                label=[Literal(f"{locName} (adres)", lang='nl')])

            mentionedLocations.append(location)

            brideRole.hasLocation = [locationRole]

        mentionedPersons.append(bride)

        if d['bride']['occupation']:
            occName = d['bride']['occupation']
            occupation = Occupation(URIRef(d['bride']['id'] + '-occupation'),
                                    label=[occName])

            occupationRole = OccupationRole(
                URIRef(d['bride']['id'] + '-occupation-role'),
                carriedIn=registrationEvent,
                carriedBy=[occupation],
                label=[Literal(f"{occName} (beroep)", lang="nl")])

            brideRole.hasOccupation = [occupationRole]

            mentionedOccupations.append(occupation)

        if d['bride']['religion']:
            religionName = d['bride']['religion']
            religion = Religion(URIRef(d['bride']['id'] + '-religion'),
                                label=[religionName])

            religionRole = PersonReligionRole(
                URIRef(d['bride']['id'] + '-religion-role'),
                carriedIn=registrationEvent,
                carriedBy=[religion],
                label=[Literal(f"{religionName} (religie)", lang="nl")])

            brideRole.hasReligion = [religionRole]

            mentionedReligions.append(religion)

        if d['bride']['exHusband']:

            pnExHusband = PersonName(
                URIRef(d['bride']['exHusband']['id'] + '-pn'),
                givenName=d['bride']['exHusband']['hasName']['givenName'],
                surnamePrefix=d['bride']['exHusband']['hasName']
                ['surnamePrefix'],
                baseSurname=d['bride']['exHusband']['hasName']['baseSurname'],
                literalName=d['bride']['exHusband']['hasName']['literalName'],
                label=d['bride']['exHusband']['hasName']['literalName'])

            exHusband = Person(URIRef(d['bride']['exHusband']['id']),
                               hasName=[pnExHusband],
                               label=[pnExHusband.label])

            exHusbandRole = EarlierHusband(
                URIRef(d['bride']['exHusband']['id'] + '-role'),
                carriedIn=registrationEvent,
                carriedBy=[exHusband],
                label=[
                    Literal(f"{pnExHusband.label} in de rol van Eerdere Man",
                            lang='nl')
                ])

            mentionedPersons.append(exHusband)

        for w in d['bride']['witnesses']:

            pnWitness = PersonName(URIRef(w['id'] + '-pn'),
                                   givenName=w['hasName']['givenName'],
                                   surnamePrefix=w['hasName']['surnamePrefix'],
                                   baseSurname=w['hasName']['baseSurname'],
                                   literalName=w['hasName']['literalName'],
                                   label=w['hasName']['literalName'])
            witness = Person(URIRef(w['id']),
                             hasName=[pnWitness],
                             label=[pnWitness.label])

            witnessRole = Getuige(
                URIRef(w['id'] + '-role'),
                carriedIn=registrationEvent,
                carriedBy=[witness],
                label=[
                    Literal(f"{pnWitness.label} in de rol van Getuige",
                            lang='nl')
                ])

            if w['relation']:

                relation = Relation(URIRef(w['id'] + '-relation'),
                                    label=[w['relation']])

                relationRole = RelationRole(
                    URIRef(w['id'] + '-relation-role'),
                    carriedIn=registrationEvent,
                    carriedBy=[relation],
                    relatedTo=witness,
                    label=[
                        Literal(f"{w['relation']} ({pnWitness.label})",
                                lang='nl')
                    ])

                brideRole.hasRelation = [relationRole]

                mentionedRelations.append(relation)

            mentionedPersons.append(witness)

        sourceIndex.mentionsPerson = mentionedPersons
        sourceIndex.mentionsLocation = mentionedLocations
        sourceIndex.mentionsEvent = mentionedEvents

        sourceIndex.mentionsOccupation = mentionedOccupations
        sourceIndex.mentionsRelation = mentionedRelations
        sourceIndex.mentionsReligion = mentionedReligions

    indexCollection.hasMember = allIndexDocuments

    graph = bindNS(graph)
    graph.bind(
        'jiwRec',
        URIRef("https://data.goldenagents.org/datasets/jaikwil/records/"))

    print("Serializing!")
    graph.serialize(path, format='trig')


if __name__ == "__main__":
    main('data/jiw/jiw_ga.json', 'trig/jiw_ga.trig')