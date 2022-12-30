# Golden Agents - SAA Pipeline

- [Golden Agents - SAA Pipeline](#golden-agents---saa-pipeline)
  - [Introduction](#introduction)
  - [Model](#model)
  - [Data](#data)
    - [City Archives of Amsterdam](#city-archives-of-amsterdam)
    - [City Archives of Amsterdam (Burial Registries, old index data)](#city-archives-of-amsterdam-burial-registries-old-index-data)
    - [Ja, ik wil!](#ja-ik-wil)
  - [Linked Open Data / RDF](#linked-open-data--rdf)
  - [License / usage](#license--usage)

## Introduction

The Golden Agents - SAA Pipeline is a set of data and scripts designed to generate linked open data in RDF format for several datasets for the Golden Agents project. The purpose of this pipeline is to make available as open data various sources of historical information about Amsterdam, such as notary archives, baptism and marriage registers, and burial registries, among others. 

This repository contains the scripts and data-(pointers) for the Golden Agents project's SAA (StadsArchief Amsterdam) pipeline that converts historical archival data from the Amsterdam City Archives into Linked Open Data (LOD/RDF) in the Golden Agents Archival Ontology ROAR++. The data is part of the Golden Agents research infrastructure.

The materials in this repository are for three datasets: 
  1. City Archives of Amsterdam (inventories + indices), 
  2. City Archives of Amsterdam (Burial Registries, old index data), and 
  3. Ja, ik wil!
The pipeline processes EAD files of relevant archive's collections and data downloaded from the archives' open data endpoint (in A2A-format), or a custom format. The result is a collection of RDF TriG files that can be loaded into a triplestore.

## Model

All data is modelled in the ROAR++ ontology. See the [`ontology`](ontology/) directory of this repository.

## Data

This repository contains the data and scripts to generate the data for three datasets in the Golden Agents project:
1. City Archives of Amsterdam
2. City Archives of Amsterdam (Burial Registries, old index data)
3. Ja, ik wil!

### City Archives of Amsterdam

RDF dataset based on the inventories and indices of the Amsterdam City Archives. It features the persons that are indexed by the archive in relation to the registration event that they are mentioned in.In total, twelve indices and their respective inventory information are covered:

   1. Index op notarieel archief
   2. Index op doopregisters
   3. Index op ondertrouwregisters
   4. Index op kwijtscheldingen
   5. Index op poorterboeken
   6. Index op confessieboeken
   7. Index op boetes op trouwen en begraven
   8. Index op begraafregisters voor 1811
   9. Index op overledenen gast pest werk spinhuis
   10. Index op averijgrossen
   11. Index op boedelpapieren
   12. Index op lidmatenregister doopsgezinde gemeente

The script in `main.py` generates the data for the 12 relevant indices of the City Archives of Amsterdam. It processes the EAD's of the relevant archival collections (see the EADs in this repository in [`data/ead/`](data/ead/)) and the A2A data downloaded from the archive's open data endpoint (OAI-PMH, see: https://opendata.picturae.com/organization/ams). 

As an example, the first file of every index is included in this repository. The full A2A data can be downloaded from the endpoint, for instance by using the `a2a.py` script in the [`a2a`](data/a2a/a2a.py) directory of this repository.

Any other data that enriches the downloaded data is included in this repository (e.g. via git-lfs). 

### City Archives of Amsterdam (Burial Registries, old index data)

The script in `begraafregisters.py` generates the data for the City Archives of Amsterdam (Burial Registries, old index data) dataset. This is an old index of the burial registers of the City Archives of Amsterdam, which was not kept in the (old) open data repository, but still contains valuable information for person and record disambiguation. This script models the data in the same format as the current A2A-data. The XML-data are available in the [`data/begraafregisters`](data/begraafregisters) directory of this repository.

### Ja, ik wil!

The script in `jiw.py` generates the data for the Ja, ik wil! dataset. This script produces a Golden Agents RDF conversion of the data that was collected in the Vele Handen Citizen Science-project 'Ja, ik wil!' [Yes, I do!]. The dataset contains the socio-economic data on grooms and brides that registered their marriage banns in Amsterdam for every fifth year between 1580 and 1810 in the Amsterdam marriage banns registers. 

The Golden Agents project has reconciled the described marriage bans to their original (scanned) source. Something that was not kept in the crowd-sourcing project. See the [`data/jiw`](data/jiw) directory for a conversion of the original data to json. 

Since this data is de facto a subset of the data in the City Archives of Amsterdam, the script produces data in the same model. A SAA-record and a JIW-record are both `IndexDocument`s of the same registration event and therefore 'mention' the same event (via the `rpp:mentionsEvent` property). 

For linksets on the level of the person, see the outcomes of the 'Processes of Creativity' case study of the Golden Agents project: https://github.com/knaw-huc/golden-agents-processes-of-creativity/tree/main/linksets (or https://doi.org/10.5281/zenodo.7478598).

The script takes in data that is based on an identical earlier as CC-BY 4.0 shared spreadsheet with the project's data. See: https://doi.org/10.25397/eur.14049842.v1 for the current public version.

## Linked Open Data / RDF

The scripts produce RDF in TriG format (https://www.w3.org/TR/trig/). These files are not included in this repository due to their size, but can be downloaded from the deposited release on Zenodo: https://doi.org/10.5281/zenodo.7662716. 

The files are available as five separate downloads:
* `ga_saa_a2a_2022.zip`
* `ga_saa_begraafregisters_2022.zip`
* `ga_saa_ead_2022.zip`
* `ga_jiw_2022.zip`: the data for the Ja, ik wil! dataset.
* `ga_ontology_thesaurus_2022.zip`: the ontology and thesaurus used in this data, as generated by these scripts. 

A live version of this data should be available at: https://data.goldenagents.org/

## License / usage

This data is licensed under CC-BY 4.0. Please also cite the [authors of the Ja, ik wil!](https://doi.org/10.25397/eur.14049842.v1) data if you use this data.

* Golden Agents project. (2022). Golden Agents - SAA Pipeline (Version v1.0) [Data set]. https://doi.org/10.5281/zenodo.7662716