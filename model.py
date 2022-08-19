"""
SAA ontology to be used in direct conversion from SAA to Golden Agents.
"""

from rdflib import Dataset, Graph, Namespace
from rdflib import XSD, RDF, RDFS, OWL, SKOS, FOAF, DCTERMS, SDO, PROV
from rdflib import URIRef, BNode, Literal

from rdfalchemy.rdfSubject import rdfSubject
from rdfalchemy import rdfSingle, rdfMultiple, rdfContainer, rdfList

AS = Namespace("http://www.w3.org/ns/activitystreams#")
bio = Namespace("http://purl.org/vocab/bio/0.1/")
geos = Namespace("http://www.opengis.net/ont/geosparql#")
hg = Namespace("http://rdf.histograph.io/")
iiif = Namespace("https://iiif.leonvanwissen.nl/iiif/2/")  # why not
oa = Namespace("http://www.w3.org/ns/oa#")
pnv = Namespace("https://w3id.org/pnv#")
# prov = Namespace("http://www.w3.org/ns/prov#")
rel = Namespace("http://purl.org/vocab/relationship/")
saaLocation = Namespace("https://data.goldenagents.org/datasets/SAA/Location/")
saa = Namespace("https://data.goldenagents.org/datasets/SAA/ontology/")
# saaNotary = Namespace("https://data.goldenagents.org/datasets/SAA/Notary/")
saaOccupation = Namespace("https://data.goldenagents.org/datasets/SAA/Occupation/")
saaOrganisation = Namespace("https://data.goldenagents.org/datasets/SAA/Organisation/")
saaPersonName = Namespace("https://data.goldenagents.org/datasets/SAA/PersonName/")
saaPerson = Namespace("https://data.goldenagents.org/datasets/SAA/Person/")
saaProperty = Namespace("https://data.goldenagents.org/datasets/SAA/Property/")

saaScan = Namespace("https://data.goldenagents.org/datasets/SAA/Scan/")
saaStreet = Namespace("https://data.goldenagents.org/datasets/SAA/Street/")
saaIntendedMarriage = Namespace(
    "https://data.goldenagents.org/datasets/SAA/IntendedMarriage/"
)
saaMarriage = Namespace("https://data.goldenagents.org/datasets/SAA/Marriage/")
# schema = Namespace("http://schema.org/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")

roar = Namespace("https://data.goldenagents.org/ontology/roar/")
ead = Namespace("https://data.goldenagents.org/datasets/saa/ead/")
a2a = Namespace("https://data.goldenagents.org/datasets/saa/a2a/")
deed = Namespace("https://archief.amsterdam/indexen/deeds/")
file = Namespace("https://archief.amsterdam/inventarissen/file/")
thes = Namespace("https://data.goldenagents.org/thesaurus/")


class SchemaPlace(rdfSubject):
    rdf_type = SDO.Place
    label = rdfMultiple(RDFS.label)


########
# ROAR #
########
class Entity(rdfSubject):
    rdf_type = PROV.Entity

    label = rdfMultiple(RDFS.label)

    prefLabel = rdfMultiple(SKOS.prefLabel)
    altLabel = rdfMultiple(SKOS.altLabel)

    description = rdfMultiple(RDFS.comment)
    identifier = rdfSingle(DCTERMS.identifier)

    isInRecord = rdfSingle(saa.isInRecord)
    wasDerivedFrom = rdfMultiple(PROV.wasDerivedFrom)

    hasTimeStamp = rdfSingle(sem.hasTimeStamp)
    hasBeginTimeStamp = rdfSingle(sem.hasBeginTimeStamp)
    hasEndTimeStamp = rdfSingle(sem.hasEndTimeStamp)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestBeginTimeStamp = rdfSingle(sem.hasLatestBeginTimeStamp)
    hasEarliestEndTimeStamp = rdfSingle(sem.hasEarliestEndTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)

    depiction = rdfMultiple(FOAF.depiction)

    memberOf = rdfSingle(roar.memberOf)
    subCollectionOf = rdfSingle(roar.subCollectionOf)

    sameAs = rdfMultiple(OWL.sameAs)

    position = rdfSingle(roar.position)


class Concept(Entity):
    rdf_type = SKOS.Concept


class Observation(Entity):
    rdf_type = roar.Observation


class Reconstruction(Entity):
    rdf_type = roar.Reconstruction


class Individual(Entity):
    rdf_type = roar.Individual


class RoleBearer(Individual):
    rdf_type = roar.RoleBearer

    participatesIn = rdfMultiple(roar.participatesIn)


class Agent(RoleBearer):
    rdf_type = roar.Agent


class Location(RoleBearer):
    rdf_type = roar.Location

    hasReligion = rdfMultiple(roar.hasReligion)


class LocationObservation(RoleBearer, Observation):
    rdf_type = roar.Location, roar.Observation


class OccupationObservation(RoleBearer, Observation):
    rdf_type = roar.Occupation, roar.Observation


class ReligionObservation(RoleBearer, Observation):
    rdf_type = roar.Religion, roar.Observation


class ReligionReconstruction(RoleBearer, Reconstruction):
    rdf_type = roar.Religion, roar.Reconstruction


class LocationReconstruction(RoleBearer, Reconstruction):
    rdf_type = roar.Location, roar.Reconstruction


class OccupationReconstruction(RoleBearer, Reconstruction):
    rdf_type = roar.Occupation, roar.Reconstruction


class Status(RoleBearer):
    rdf_type = roar.Status


class Person(Agent):
    rdf_type = roar.Person

    hasName = rdfMultiple(pnv.hasName, range_type=pnv.PersonName)  # resource


class PersonName(Entity):
    rdf_type = pnv.PersonName
    label = rdfSingle(RDFS.label)

    # These map to A2A
    literalName = rdfSingle(pnv.literalName)
    givenName = rdfSingle(pnv.givenName)
    surnamePrefix = rdfSingle(pnv.surnamePrefix)
    baseSurname = rdfSingle(pnv.baseSurname)

    # These do not
    prefix = rdfSingle(pnv.prefix)
    disambiguatingDescription = rdfSingle(pnv.disambiguatingDescription)
    patronym = rdfSingle(pnv.patronym)
    surname = rdfSingle(pnv.surname)

    # # Extra for the notarial acts
    # personId = rdfSingle(saa.personId)
    # scanName = rdfSingle(saa.scanName)
    # scanPosition = rdfSingle(saa.scanPosition)
    # uuidName = rdfSingle(saa.uuidName)


class TimeInterval(Entity):
    rdf_type = roar.TimeInterval

    start = rdfSingle(roar.start)
    end = rdfSingle(roar.end)


class Place(Entity):
    rdf_type = roar.Place


class Religion(Entity):
    rdf_type = roar.Religion


class Document(Entity):
    rdf_type = roar.Document

    author = rdfMultiple(roar.author)
    publisher = rdfMultiple(roar.publisher)
    temporal = rdfSingle(DCTERMS.temporal)

    partOf = rdfSingle(roar.partOf)

    createdBy = rdfMultiple(roar.createdBy)
    createdAt = rdfSingle(roar.createdAt)
    createdIn = rdfSingle(roar.createdIn)

    indexOf = rdfSingle(roar.indexOf)

    mentionsPerson = rdfMultiple(roar.mentionsPerson)
    mentionsObject = rdfMultiple(roar.mentionsObject)
    mentionsEvent = rdfMultiple(roar.mentionsEvent)
    mentionsLocation = rdfMultiple(roar.mentionsLocation)
    mentionsOccupation = rdfMultiple(roar.mentionsOccupation)
    mentionsReligion = rdfMultiple(roar.mentionsReligion)
    mentionsRelation = rdfMultiple(roar.mentionsRelation)
    mentionsStatus = rdfMultiple(roar.mentionsStatus)
    mentionsRole = rdfMultiple(roar.mentionsRole)

    hasScan = rdfMultiple(roar.hasScan)  # physical document
    onScan = rdfMultiple(roar.onScan)  # index document

    onPage = rdfSingle(roar.onPage)

    inLanguage = rdfSingle(roar.inLanguage)


class IndexDocument(Document):
    rdf_type = roar.IndexDocument

    cancelled = rdfSingle(roar.cancelled)


class Collection(Document):
    rdf_type = roar.Collection

    language = rdfMultiple(DCTERMS.language)
    # authority = rdfMultiple(DCTERMS.authority)
    creator = rdfMultiple(DCTERMS.creator)

    hasGroupingCriteria = rdfMultiple(roar.hasGroupingCriteria)
    hasSubCollection = rdfMultiple(roar.hasSubCollection)
    hasMember = rdfMultiple(roar.hasMember)


class InventoryCollection(Collection):
    rdf_type = roar.InventoryCollection


class IndexCollection(Collection):
    rdf_type = roar.IndexCollection


class ScanCollection(Collection):
    rdf_type = roar.ScanCollection


class BookIndex(IndexCollection):
    rdf_type = roar.BookIndex


class InventoryBook(InventoryCollection):
    rdf_type = roar.InventoryBook


class GroupingCriterion(Entity):
    rdf_type = roar.GroupingCriterion

    hasFilter = rdfSingle(roar.hasFilter)
    hasFilterValue = rdfMultiple(roar.hasFilterValue)
    hasFilterStart = rdfSingle(roar.hasFilterStart)
    hasFilterEnd = rdfSingle(roar.hasFilterEnd)


class Event(Entity):
    rdf_type = roar.Event

    hasInput = rdfMultiple(roar.hasInput)
    hasOutput = rdfMultiple(roar.hasOutput)

    hasPlace = rdfMultiple(roar.hasPlace)

    hasReligion = rdfMultiple(roar.hasReligion)


class RegistrationEvent(Event):
    rdf_type = roar.RegistrationEvent

    registers = rdfSingle(roar.registers, range_type=roar.Event)


class DocumentCreation(Event):
    rdf_type = roar.DocumentCreation


class DocumentType(Entity):
    rdf_type = roar.DocumentType
    subClassOf = rdfSingle(RDFS.subClassOf)


class EventType(Entity):
    rdf_type = roar.EventType
    subClassOf = rdfSingle(RDFS.subClassOf)


class Geboorte(Event):
    rdf_type = thes.Geboorte


class Role(Entity):
    rdf_type = roar.Role

    carriedIn = rdfSingle(roar.carriedIn)
    carriedBy = rdfMultiple(roar.carriedBy)

    hasRelation = rdfMultiple(roar.hasRelation)
    hasLocation = rdfMultiple(roar.hasLocation)
    hasReligion = rdfMultiple(roar.hasReligion)
    hasOccupation = rdfMultiple(roar.hasOccupation)
    hasStatus = rdfMultiple(roar.hasStatus)

    age = rdfSingle(roar.age)
    literate = rdfSingle(roar.literate)


class RoleType(Entity):
    rdf_type = roar.RoleType
    subClassOf = rdfSingle(RDFS.subClassOf)


class PersonReligionRole(Role):
    rdf_type = thes.Persoonsreligie
    subClassOf = roar.Role


class Relation(Entity):
    rdf_type = roar.Relation


class Geregistreerde(Role):
    rdf_type = thes.Geregistreerde
    subClassOf = roar.Role


class NotaryRole(Role):
    rdf_type = thes.Notaris
    subClassOf = roar.Role


class ChildRole(Role):
    rdf_type = thes.Kind
    subClassOf = roar.Role


class EarlierHusband(Role):
    rdf_type = thes.EerdereMan
    subClassOf = roar.Role


class EarlierWife(Role):
    rdf_type = thes.EerdereVrouw
    subClassOf = roar.Role


class Bruid(Role):
    rdf_type = thes.Bruid
    subClassOf = roar.Role


class Bruidegom(Role):
    rdf_type = thes.Bruidegom
    subClassOf = roar.Role


class Getuige(Role):
    rdf_type = thes.Getuige
    subClassOf = roar.Role


class Verdachte(Role):
    rdf_type = thes.Verdachte
    subClassOf = roar.Role


class OccupationRole(Role):
    rdf_type = thes.Beroep
    subClassOf = roar.Role


class HuwelijkseStaat(Role):
    rdf_type = thes.Huwelijksestaat

    subClassOf = roar.Role


class LocationRole(Role):
    rdf_type = thes.Locatieomschrijving

    subClassOf = roar.Role


class OriginRole(Role):
    rdf_type = thes.Herkomstlocatie

    subClassOf = roar.Role


class WorkLocationRole(Role):
    rdf_type = thes.Werklocatie

    subClassOf = roar.Role


class AddressRole(Role):
    rdf_type = thes.Adresomschrijving


class RelationRole(Role):
    rdf_type = thes.Relatieomschrijving

    relatedTo = rdfSingle(roar.relatedTo)


class CollectionCreation(Event):
    rdf_type = roar.DocumentCreation, roar.DocumentArchiving


class ArchiverAndCreatorRole(Role):
    rdf_type = roar.Archiver, roar.Creator


class ArchivalDocumentRole(Role):
    rdf_type = roar.ArchivalDocument


# Scans


class Scan(Entity):
    rdf_type = roar.Scan

    # # partOf a collection

    # depiction = rdfSingle(FOAF.depiction)
    # url = rdfSingle(saa.url)

    # imageFilename = rdfSingle(saa.imageFilename)
    # imageWidth = rdfSingle(saa.imageWidth)
    # imageHeight = rdfSingle(saa.imageHeight)

    # regions = rdfMultiple(saa.regions)

    # items = rdfList(AS.items)  # rdf:Collection
    # prev = rdfSingle(AS.prev)
    # next = rdfSingle(AS.next)


class SpreadScan(Scan):
    rdf_type = roar.SpreadScan


#############
# SAA Index #
#############


class IndexRecord(Entity):
    rdf_type = saa.IndexRecord
    identifier = rdfSingle(saa.identifier)

    date = rdfSingle(saa.date)  # datering? [=sourceDate?]

    actType = rdfSingle(saa.actType)
    registrationDate = rdfSingle(saa.registrationDate)
    language = rdfSingle(saa.language)

    inventoryNumber = rdfSingle(saa.inventoryNumber)
    collectionNumber = rdfSingle(saa.collectionNumber)
    sectionNumber = rdfSingle(saa.sectionNumber)
    sourceReference = rdfSingle(saa.sourceReference)
    urlScan = rdfMultiple(saa.urlScan)

    mentionsRegisteredName = rdfMultiple(saa.mentionsRegisteredName)
    mentionsLocation = rdfMultiple(saa.mentionsLocation, range_type=saa.Location)

    hasEvent = rdfMultiple(saa.hasEvent)


class IndexOpNotarieelArchief(IndexRecord):
    rdf_type = saa.IndexOpNotarieelArchief
    mentionsNotary = rdfMultiple(saa.mentionsNotary)
    actNumber = rdfSingle(saa.actNumber)


class IndexOpDoopregisters(IndexRecord):
    rdf_type = saa.IndexOpDoopregisters

    baptismDate = rdfSingle(saa.baptismDate)
    birthDate = rdfSingle(saa.birthDate)

    church = rdfSingle(saa.church)
    religion = rdfSingle(saa.religion)

    mentionsFatherName = rdfMultiple(saa.mentionsFatherName)
    mentionsMotherName = rdfMultiple(saa.mentionsMotherName)
    mentionsChildName = rdfMultiple(saa.mentionsChildName)

    mentionsWitnessName = rdfMultiple(saa.mentionsWitnessName)


class IndexOpOndertrouwregisters(IndexRecord):
    rdf_type = saa.IndexOpOndertrouwregisters

    mentionsGroomName = rdfMultiple(saa.mentionsGroomName)
    mentionsBrideName = rdfMultiple(saa.mentionsBrideName)

    mentionsEarlierHusbandName = rdfMultiple(saa.mentionsEarlierHusbandName)
    mentionsEarlierWifeName = rdfMultiple(saa.mentionsEarlierWifeName)

    # cancelled = rdfSingle(saa.cancelled)


class IndexOpKwijtscheldingen(IndexRecord):
    rdf_type = saa.IndexOpKwijtscheldingen

    mentionsSellerName = rdfMultiple(saa.mentionsSeller)
    mentionsBuyerName = rdfMultiple(saa.mentionsBuyer)

    mentionsSellerOrganisation = rdfMultiple(saa.mentionsSellerOrganisation)
    mentionsBuyerOrganisation = rdfMultiple(saa.mentionsBuyerOrganisation)

    mentionsStreet = rdfSingle(saa.mentionsStreet)
    mentionsOriginalStreet = rdfSingle(saa.mentionsOriginalStreet)

    mentionsProperty = rdfSingle(saa.mentionsProperty)


class IndexOpPoorterboeken(IndexRecord):
    rdf_type = saa.IndexOpPoorterboeken

    mentionsOccupation = rdfSingle(saa.mentionsOccupation)

    mentionsOriginalLocation = rdfSingle(saa.mentionsOriginalLocation)


class IndexOpConfessieboeken(IndexRecord):
    rdf_type = saa.IndexOpConfessieboeken

    mentionsSuspectName = rdfMultiple(saa.mentionsSuspect)
    mentionsOrigin = rdfSingle(saa.mentionsOrigin)
    confessionDate = rdfSingle(saa.confessionDate)


class IndexOpBoetesOpTrouwenEnBegraven(IndexRecord):
    rdf_type = saa.IndexOpBoetesOpTrouwenEnBegraven

    mentionsGroomName = rdfMultiple(saa.mentionsGroom)
    mentionsBrideName = rdfMultiple(saa.mentionsBride)

    mentionsDeceasedName = rdfMultiple(saa.mentionsDeceased)


class IndexOpBegraafregisters(IndexRecord):
    rdf_type = saa.IndexOpBegraafregisters

    burialDate = rdfSingle(saa.burialDate)

    cemetery = rdfSingle(saa.cemetery)

    mentionsBuriedName = rdfMultiple(saa.mentionsBuriedName)

    relationInformation = rdfSingle(saa.relationInformation)


class Inventory(Entity):
    notary = rdfMultiple(saa.notary)


class Organisation(Entity):
    rdf_type = saa.Organisation

    label = rdfMultiple(RDFS.label)


class Notary(Person):
    rdf_type = saa.Notary
    collaboratesWith = rdfMultiple(rel.collaboratesWith, range_type=saa.Person)

    notaryOfSectionNumber = rdfSingle(saa.notaryOfSectionNumber)
    notaryOfInventoryNumber = rdfMultiple(saa.notaryOfInventoryNumber)


class SchemaOccupation(Entity):
    rdf_type = SDO.Occupation

    occupationalCategory = rdfMultiple(
        SDO.occupationalCategory, range_type=SDO.CategoryCode
    )


class CategoryCode(Entity):
    rdf_type = SDO.CategoryCode
    inCodeSet = rdfSingle(SDO.inCodeSet, range_type=SDO.CategoryCodeSet)
    codeValue = rdfSingle(SDO.codeValue)

    name = rdfMultiple(SDO.name)


class CategoryCodeSet(Entity):
    rdf_type = SDO.CategoryCodeSet
    name = rdfMultiple(SDO.name)

    # {
    #     "@context": "http://schema.org/",
    #     "@type": "Occupation",
    #     "name": "Film actor",
    #     "occupationalCategory": {
    #         "@type": "CategoryCode",
    #         "inCodeSet": {
    #             "@type": "CategoryCodeSet",
    #             "name": "HISCO"
    #         },
    #         "codeValue": "17320",
    #         "name": "Actor"
    #     }
    # }


#############
# Locations #
#############
# class Location(Entity):
#     rdf_type = saa.Location

#     altLabel = rdfMultiple(SKOS.altLabel)
#     sameAs = rdfMultiple(OWL.sameAs)


class Street(Location):
    rdf_type = saa.Street


#################
# Notarial acts #
#################
class HuwelijkseVoorwaarden(IndexOpNotarieelArchief):
    rdf_type = saa.HuwelijkseVoorwaarden


class NonPrejuditie(IndexOpNotarieelArchief):
    rdf_type = saa.NonPrejuditie


class Voogdij(IndexOpNotarieelArchief):
    rdf_type = saa.Voogdij


class Overig(IndexOpNotarieelArchief):
    rdf_type = saa.Overig


class Renunciatie(IndexOpNotarieelArchief):
    rdf_type = saa.Renunciatie


class Compagnieschap(IndexOpNotarieelArchief):
    rdf_type = saa.Compagnieschap


class Bijlbrief(IndexOpNotarieelArchief):
    rdf_type = saa.Bijlbrief


class Testament(IndexOpNotarieelArchief):
    rdf_type = saa.Testament


class Trouwbelofte(IndexOpNotarieelArchief):
    rdf_type = saa.Trouwbelofte


class Akkoord(IndexOpNotarieelArchief):
    rdf_type = saa.Akkoord


class Scheepsverklaring(IndexOpNotarieelArchief):
    rdf_type = saa.Scheepsverklaring


class Contract(IndexOpNotarieelArchief):
    rdf_type = saa.Contract


class Boedelscheiding(IndexOpNotarieelArchief):
    rdf_type = saa.Boedelscheiding


class Bevrachtingscontract(IndexOpNotarieelArchief):
    rdf_type = saa.Bevrachtingscontract


class Uitspraak(IndexOpNotarieelArchief):
    rdf_type = saa.Uitspraak


class Attestatie(IndexOpNotarieelArchief):
    rdf_type = saa.Attestatie


class Koop(IndexOpNotarieelArchief):
    rdf_type = saa.Koop


class Wisselprotest(IndexOpNotarieelArchief):
    rdf_type = saa.Wisselprotest


class Obligatie(IndexOpNotarieelArchief):
    rdf_type = saa.Obligatie


class Transport(IndexOpNotarieelArchief):
    rdf_type = saa.Transport


class Onbekend(IndexOpNotarieelArchief):
    rdf_type = saa.Onbekend


class Borgtocht(IndexOpNotarieelArchief):
    rdf_type = saa.Borgtocht


class Procuratie(IndexOpNotarieelArchief):
    rdf_type = saa.Procuratie


class Insinuatie(IndexOpNotarieelArchief):
    rdf_type = saa.Insinuatie


class Interrogatie(IndexOpNotarieelArchief):
    rdf_type = saa.Interrogatie


class Hypotheek(IndexOpNotarieelArchief):
    rdf_type = saa.Procuratie


class Bestek(IndexOpNotarieelArchief):
    rdf_type = saa.Bestek


class BewijsAanMinderjarigen(IndexOpNotarieelArchief):
    rdf_type = saa.BewijsAanMinderjarigen


class Kwitantie(IndexOpNotarieelArchief):
    rdf_type = saa.Kwitantie


class Bodemerij(IndexOpNotarieelArchief):
    rdf_type = saa.Bodemerij


class Boedelinventaris(IndexOpNotarieelArchief):
    rdf_type = saa.Boedelinventaris


class ConventieEchtscheiding(IndexOpNotarieelArchief):
    rdf_type = saa.ConventieEchtscheiding


class Revocatie(IndexOpNotarieelArchief):
    rdf_type = saa.Revocatie


class Consent(IndexOpNotarieelArchief):
    rdf_type = saa.Consent


class Machtiging(IndexOpNotarieelArchief):
    rdf_type = saa.Machtiging


class Cessie(IndexOpNotarieelArchief):
    rdf_type = saa.Cessie


class AkteVanExecuteurschap(IndexOpNotarieelArchief):
    rdf_type = saa.AkteVanExecuteurschap


class Huur(IndexOpNotarieelArchief):
    rdf_type = saa.Huur


class Schenking(IndexOpNotarieelArchief):
    rdf_type = saa.Schenking


class Beraad(IndexOpNotarieelArchief):
    rdf_type = saa.Beraad


###############
# Annotations #
###############


class Annotation(Entity):
    rdf_type = oa.Annotation
    hasTarget = rdfSingle(oa.hasTarget)

    bodyValue = rdfSingle(oa.bodyValue)

    hasBody = rdfSingle(oa.hasBody)  # or multiple?

    motivatedBy = rdfSingle(oa.motivatedBy)

    depiction = rdfSingle(FOAF.depiction)


class SpecificResource(Entity):
    rdf_type = oa.SpecificResource

    hasSource = rdfSingle(oa.hasSource)
    hasSelector = rdfSingle(oa.hasSelector)
    hasState = rdfSingle(oa.hasState)
    hasPurpose = rdfSingle(oa.hasPurpose)


class Selector(Entity):
    rdf_type = oa.Selector


class FragmentSelector(Selector):
    rdf_type = oa.FragmentSelector

    conformsTo = rdfSingle(DCTERMS.conformsTo)
    value = rdfSingle(RDF.value)


class TextQuoteSelector(Selector):
    rdf_type = oa.TextQuoteSelector


class TextPositionSelector(Selector):
    rdf_type = oa.TextPositionSelector


############
# Geometry #
############


class Geometry(Entity):
    rdf_type = geos.Geometry

    # geosparql
    asWKT = rdfSingle(geos.asWKT)

    hasTimeStamp = rdfSingle(sem.hasTimeStamp)
    hasBeginTimeStamp = rdfSingle(sem.hasBeginTimeStamp)
    hasEndTimeStamp = rdfSingle(sem.hasEndTimeStamp)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestBeginTimeStamp = rdfSingle(sem.hasLatestBeginTimeStamp)
    hasEarliestEndTimeStamp = rdfSingle(sem.hasEarliestEndTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)


class Property(Entity):
    rdf_type = saa.Property

    hasGeometry = rdfMultiple(geos.hasGeometry)
    liesIn = rdfSingle(hg.liesIn)

    propertyType = rdfMultiple(saa.propertyType)
    legalFraction = rdfMultiple(saa.legalFraction)

    propertyNameReference = rdfMultiple(saa.propertyNameReference)


class PropertyNameReference(Entity):
    rdf_type = saa.PropertyNameReference

    positionReference = rdfSingle(saa.positionReference)
    nameReferenceType = rdfSingle(saa.name_type)


class HgArea(Entity):
    rdf_type = hg.Area
    hasGeometry = rdfMultiple(geos.hasGeometry)
