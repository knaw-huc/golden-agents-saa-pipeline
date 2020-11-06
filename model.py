"""
SAA ontology to be used in direct conversion from SAA to Golden Agents. 
"""

from rdflib import Dataset, Graph, Namespace
from rdflib import XSD, RDF, RDFS, OWL
from rdflib import URIRef, BNode, Literal

from rdfalchemy.rdfSubject import rdfSubject
from rdfalchemy import rdfSingle, rdfMultiple, rdfContainer, rdfList
from rdflib.namespace import DCTERMS

AS = Namespace("http://www.w3.org/ns/activitystreams#")
bio = Namespace("http://purl.org/vocab/bio/0.1/")
dcterms = Namespace("http://purl.org/dc/terms/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
geos = Namespace("http://www.opengis.net/ont/geosparql#")
hg = Namespace("http://rdf.histograph.io/")
iiif = Namespace("https://iiif.leonvanwissen.nl/iiif/2/")  # why not
oa = Namespace("http://www.w3.org/ns/oa#")
pnv = Namespace('https://w3id.org/pnv#')
prov = Namespace("http://www.w3.org/ns/prov#")
rel = Namespace("http://purl.org/vocab/relationship/")
saaLocation = Namespace("https://data.goldenagents.org/datasets/SAA/Location/")
saa = Namespace("https://data.goldenagents.org/datasets/SAA/ontology/")
# saaNotary = Namespace("https://data.goldenagents.org/datasets/SAA/Notary/")
saaOccupation = Namespace(
    "https://data.goldenagents.org/datasets/SAA/Occupation/")
saaOrganisation = Namespace(
    "https://data.goldenagents.org/datasets/SAA/Organisation/")
saaPersonName = Namespace(
    "https://data.goldenagents.org/datasets/SAA/PersonName/")
saaPerson = Namespace("https://data.goldenagents.org/datasets/SAA/Person/")
saaProperty = Namespace("https://data.goldenagents.org/datasets/SAA/Property/")

saaScan = Namespace("https://data.goldenagents.org/datasets/SAA/Scan/")
saaStreet = Namespace("https://data.goldenagents.org/datasets/SAA/Street/")
saaIntendedMarriage = Namespace(
    "https://data.goldenagents.org/datasets/SAA/IntendedMarriage/")
saaMarriage = Namespace("https://data.goldenagents.org/datasets/SAA/Marriage/")
schema = Namespace('http://schema.org/')
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
skos = Namespace('http://www.w3.org/2004/02/skos/core#')

roar = Namespace("https://data.goldenagents.org/ontology/roar/")
a2a = Namespace("https://data.goldenagents.org/datasets/saa/a2a/")


########
# ROAR #
########
class Entity(rdfSubject):
    rdf_type = prov.Entity

    label = rdfMultiple(RDFS.label)
    description = rdfMultiple(RDFS.comment)
    identifier = rdfSingle(roar.identifier)

    isInRecord = rdfSingle(saa.isInRecord)
    wasDerivedFrom = rdfMultiple(prov.wasDerivedFrom)

    hasTimeStamp = rdfSingle(sem.hasTimeStamp)
    hasBeginTimeStamp = rdfSingle(sem.hasBeginTimeStamp)
    hasEndTimeStamp = rdfSingle(sem.hasEndTimeStamp)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestBeginTimeStamp = rdfSingle(sem.hasLatestBeginTimeStamp)
    hasEarliestEndTimeStamp = rdfSingle(sem.hasEarliestEndTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)

    depiction = rdfMultiple(foaf.depiction)


class Agent(Entity):
    rdf_type = roar.Agent


class Document(Entity):
    rdf_type = roar.Document

    author = rdfMultiple(roar.author)
    publisher = rdfMultiple(roar.publisher)
    temporal = rdfSingle(DCTERMS.temporal)

    partOf = rdfSingle(roar.partOf)

    createdBy = rdfMultiple(roar.createdBy)
    createdAt = rdfSingle(roar.createdAt)


class DocumentCollection(Document):
    rdf_type = roar.DocumentCollection

    language = rdfMultiple(roar.language)
    repository = rdfMultiple(roar.repository)
    origination = rdfMultiple(roar.origination)

    hasGroupingCriteria = rdfMultiple(roar.hasGroupingCriteria)
    hasSubCollection = rdfMultiple(roar.hasSubCollection)
    hasMember = rdfMultiple(roar.hasMember)


class Book(DocumentCollection):
    rdf_type = roar.Book


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


class Role(Entity):
    rdf_type = roar.Role

    carriedIn = rdfSingle(roar.carriedIn)
    carriedBy = rdfMultiple(roar.carriedBy)


class CollectionCreation(Event):
    rdf_type = roar.DocumentCreation, roar.DocumentArchiving


class ArchiverAndCreatorRole(Role):
    rdf_type = roar.Archiver, roar.Creator


class ArchivalDocumentRole(Role):
    rdf_type = roar.ArchivalDocument


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

    description = rdfSingle(saa.description)

    mentionsRegisteredName = rdfMultiple(saa.mentionsRegisteredName)
    mentionsLocation = rdfMultiple(saa.mentionsLocation,
                                   range_type=saa.Location)

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

    cancelled = rdfSingle(saa.cancelled)


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


class Person(Entity):
    rdf_type = saa.Person

    hasName = rdfMultiple(pnv.hasName, range_type=pnv.PersonName)  # resource

    scanName = rdfSingle(saa.scanName)
    scanPosition = rdfSingle(saa.scanPosition)

    birth = rdfSingle(bio.birth)
    death = rdfSingle(bio.death)
    event = rdfMultiple(bio.event)

    gender = rdfSingle(schema.gender)

    mother = rdfSingle(bio.mother)
    father = rdfSingle(bio.father)
    child = rdfSingle(bio.child)

    spouse = rdfMultiple(schema.spouse)
    parent = rdfMultiple(schema.parent)
    children = rdfMultiple(schema.children)

    hasOccupation = rdfMultiple(schema.hasOccupation)


class Notary(Person):
    rdf_type = saa.Notary
    collaboratesWith = rdfMultiple(rel.collaboratesWith, range_type=saa.Person)

    notaryOfSectionNumber = rdfSingle(saa.notaryOfSectionNumber)
    notaryOfInventoryNumber = rdfMultiple(saa.notaryOfInventoryNumber)


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

    # Extra for the notarial acts
    personId = rdfSingle(saa.personId)
    scanName = rdfSingle(saa.scanName)
    scanPosition = rdfSingle(saa.scanPosition)
    uuidName = rdfSingle(saa.uuidName)


class Occupation(Entity):
    rdf_type = saa.Occupation

    occupationalCategory = rdfMultiple(schema.occupationalCategory,
                                       range_type=schema.CategoryCode)


class CategoryCode(Entity):
    rdf_type = schema.CategoryCode
    inCodeSet = rdfSingle(schema.inCodeSet, range_type=schema.CategoryCodeSet)
    codeValue = rdfSingle(schema.codeValue)

    name = rdfMultiple(schema.name)


class CategoryCodeSet(Entity):
    rdf_type = schema.CategoryCodeSet
    name = rdfMultiple(schema.name)

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
class Location(Entity):
    rdf_type = saa.Location

    altLabel = rdfMultiple(skos.altLabel)
    sameAs = rdfMultiple(OWL.sameAs)


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
class Scan(Entity):
    rdf_type = (saa.Scan, AS.OrderedCollectionPage)

    # partOf a collection

    depiction = rdfSingle(foaf.depiction)
    url = rdfSingle(saa.url)

    imageFilename = rdfSingle(saa.imageFilename)
    imageWidth = rdfSingle(saa.imageWidth)
    imageHeight = rdfSingle(saa.imageHeight)

    regions = rdfMultiple(saa.regions)

    items = rdfList(AS.items)  # rdf:Collection
    prev = rdfSingle(AS.prev)
    next = rdfSingle(AS.next)


class Annotation(Entity):
    rdf_type = oa.Annotation
    hasTarget = rdfSingle(oa.hasTarget)

    bodyValue = rdfSingle(oa.bodyValue)

    hasBody = rdfSingle(oa.hasBody)  # or multiple?

    motivatedBy = rdfSingle(oa.motivatedBy)

    depiction = rdfSingle(foaf.depiction)


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

    conformsTo = rdfSingle(dcterms.conformsTo)
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

    #geosparql
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