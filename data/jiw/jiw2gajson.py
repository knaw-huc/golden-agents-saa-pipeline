import json
import pandas as pd


def parseInversePersonName(nameString):
    """
    Cut a name into individual parts.
    """

    if type(nameString) != str or nameString == "":
        return None, None, None, None

    pns = []
    labels = []

    if ", " in nameString:
        baseSurname, givenName = nameString.rsplit(", ", 1)

        if "[" in givenName:
            givenName, surnamePrefix = givenName.split("[")
            surnamePrefix = surnamePrefix[:-1]
        else:
            surnamePrefix = None

        givenName = givenName.strip()

    else:
        givenName = None
        surnamePrefix = None
        baseSurname = nameString

    literalName = " ".join(i for i in [givenName, surnamePrefix, baseSurname] if i)

    if not literalName:
        literalName = "Unknown"

    return [
        i if i != "" else None
        for i in [givenName, surnamePrefix, baseSurname, literalName]
    ]


def parsePersonName(nameString):

    if type(nameString) != str or nameString.startswith("_") or nameString == "":
        return None, None, None, None, None

    dets = ["van", "de", "den", "des", "der", "ten", "l'", "d'"]
    prefixes = ["Mr."]
    suffixes = ["Jr.", "Sr."]
    patronymfix = ("sz", "sz.", "szoon", "dr", "dr.")

    # Correcting syntax errors
    nameString = nameString.replace(".", ". ")
    nameString = nameString.replace("'", "' ")
    nameString = nameString.replace("  ", " ")

    # Tokenise
    tokens = nameString.split(" ")
    tokens = [i.lower() for i in tokens]
    tokens = [i.title() if i not in dets else i for i in tokens]
    nameString = " ".join(
        tokens
    )  # ALL CAPS to normal name format (e.g. Mr. Jan van Tatenhove)
    nameString = nameString.replace("' ", "'")  # clunk back the apostrophe to the name

    # -fixes
    surnamePrefix = " ".join(i for i in tokens if i in dets).strip()
    prefix = " ".join(i for i in tokens if i in prefixes).strip()
    suffix = " ".join(i for i in tokens if i in suffixes).strip()

    name_removed_fix = " ".join(
        i for i in tokens if i not in prefixes and i not in suffixes
    )

    if surnamePrefix and surnamePrefix in name_removed_fix:
        name = name_removed_fix.split(surnamePrefix)
        givenName = name[0].strip()
        baseSurname = name[1].strip()

    else:
        name = name_removed_fix.split(" ", 1)
        givenName = name[0]
        baseSurname = name[1] if len(name) > 1 else ""

    baseSurname_split = baseSurname.split(" ")
    givenName_split = givenName.split(" ")

    # build first name, family name, patronym and ignore -fixes
    givenName = " ".join(
        i for i in givenName_split if not i.endswith(patronymfix)
    ).strip()
    baseSurname = " ".join(
        i for i in baseSurname_split if not i.endswith(patronymfix)
    ).strip()
    patronym = " ".join(
        i for i in givenName_split + baseSurname_split if i.endswith(patronymfix)
    ).strip()

    literalName = " ".join(
        tokens
    ).strip()  # ALL CAPS to normal name format (e.g. Mr. Jan van Tatenhove)

    if not literalName:
        literalName = "Unknown"

    return [
        i if i != "" else None
        for i in [givenName, patronym, surnamePrefix, baseSurname, literalName]
    ]


if __name__ == "__main__":

    df = pd.read_csv("JIW.csv", low_memory=False)
    df = df.where(pd.notnull(df), None)

    with open(
        "/home/leon/Documents/Golden_Agents/saaA2A/data/concordance/source2physicalUri.json"
    ) as infile:
        source2physicalUri = json.load(infile)

    with open(
        "/home/leon/Documents/Golden_Agents/saaA2A/data/concordance/saaid2source.json"
    ) as infile:
        saaid2source = json.load(infile)

    with open(
        "/home/leon/Documents/Golden_Agents/saaA2A/data/jiw/jiwid2saaid.json"
    ) as infile:
        jiwid2saaid = json.load(infile)

    # saaId (old)
    df["ga_saaId"] = [jiwid2saaid.get(i, "") for i in df["ID_record"]]

    # deed_uuid (new)
    df["ga_saa_deed_uuid"] = [saaid2source.get(i, "") for i in df["ga_saaId"]]

    # connect it to physical book and index on this book (inventory)
    df["ga_saa_inventory_uri"] = [
        source2physicalUri.get(i, "") for i in df["ga_saa_deed_uuid"]
    ]
    df["ga_saa_inventoryIndex_uri"] = [
        i.replace(
            "https://data.goldenagents.org/datasets/saa/ead/",
            "https://archief.amsterdam/inventarissen/file/",
        )
        for i in df["ga_saa_inventory_uri"]
    ]

    # add registrationEvent
    df["ga_saa_registrationEvent_uri"] = [
        f"https://archief.amsterdam/indexen/deeds/{i}?event=Event1" if i else ""
        for i in df["ga_saa_deed_uuid"]
    ]

    data = []

    for i in df.to_dict(orient="records"):

        uri = "https://data.goldenagents.org/datasets/jaikwil/records/" + i["ID_record"]

        d = {
            "id": uri,
            "partOf": i["ga_saa_inventory_uri"],
            "indexOf": i["ga_saa_inventory_uri"] + "#" + i["ga_saa_deed_uuid"],
            "mentionsRegistrationEvent": i["ga_saa_registrationEvent_uri"],
            "date": i["inschrijfdatum"],
            "location": i["locatie"],
            "cancelled": True if i["geannuleerd"] == 1 else False,
            "comments": i["opmerkingen"],
        }

        ## groom

        givenName, surnamePrefix, baseSurname, literalName = parseInversePersonName(
            i["bruidegom"]
        )

        if not literalName:
            literalName = "Unknown"

        groom = {
            "id": uri + "-groom",
            "hasName": {
                "givenName": givenName,
                "surnamePrefix": surnamePrefix,
                "baseSurname": baseSurname,
                "literalName": literalName,
            },
            "age": int(i["groom_age_cleaned_yrsonly"])
            if i["groom_age_cleaned_yrsonly"].isdigit()
            else None,
            "religion": i["bruidegom_geloof"],
            "occupation": i["bruidegom_beroep"],
            "occupation_modern": i["groom_occupation_current"],
            "occupation_hisco": i["Groom_occupation-HIScode"],
            "origin": i["bruidegom_herkomst"],
            "homeLocation": i["bruidegom_adres"],
            "parents_deceased": True if i["bruidegom_ouders_overleden"] == 1 else False,
            "marital_status_modern": i["groom_marital_status_standardize"],
            "signature": True if i["bruidegom_handtekening"] == 1 else False,
        }

        groom_witnesses = []
        for n, column in enumerate(
            [
                "bruidegom_getuige_1",
                "bruidegom_getuige_2",
                "bruidegom_getuige_3",
                "bruidegom_getuige_4",
            ],
            1,
        ):

            (
                givenName,
                patronym,
                surnamePrefix,
                baseSurname,
                literalName,
            ) = parsePersonName(i[column])

            relation = i[column.replace("_getuige_", "_getuige_relatie_")]
            if type(relation) == str and "Niet gespecificeerd" in relation:
                relation = None
            elif relation == "Anders":
                relation = i[f"bruidegom_getuige_relatie_{n}_anders"]

            if n == 1 and not i["groom_wn1_relation_standardized"].startswith("_"):
                relation_modern = i["groom_wn1_relation_standardized"]
            else:
                relation_modern = None

            witness_data = {
                "id": uri + "-groom-witness-" + str(n),
                "relation": relation,
                "relation_modern": relation_modern,
                "hasName": {
                    "givenName": givenName,
                    "patronym": patronym,
                    "surnamePrefix": surnamePrefix,
                    "baseSurname": baseSurname,
                    "literalName": literalName,
                },
            }
            if literalName:
                groom_witnesses.append(witness_data)

        groom["witnesses"] = groom_witnesses

        # ex_groom
        givenName, surnamePrefix, baseSurname, literalName = parseInversePersonName(
            i["bruidegom_ex"]
        )

        groom_ex = {
            "id": uri + "-groom-ex",
            "hasName": {
                "givenName": givenName,
                "surnamePrefix": surnamePrefix,
                "baseSurname": baseSurname,
                "literalName": literalName,
            },
        }
        if literalName:
            groom["exWife"] = groom_ex
        else:
            groom["exWife"] = None

        for k, v in groom.items():
            if type(v) == str and v.startswith(("_", "{")):
                groom[k] = None

        d["groom"] = groom

        ## bride

        givenName, surnamePrefix, baseSurname, literalName = parseInversePersonName(
            i["bruid"]
        )

        if not literalName:
            literalName = "Unknown"

        bride = {
            "id": uri + "-bride",
            "hasName": {
                "givenName": givenName,
                "surnamePrefix": surnamePrefix,
                "baseSurname": baseSurname,
                "literalName": literalName,
            },
            "age": int(i["bride_age_cleaned_yrsonly"])
            if i["bride_age_cleaned_yrsonly"].isdigit()
            else None,
            "religion": i["bruid_geloof"],
            "occupation": i["bruid_beroep"],
            "occupation_modern": None,
            "occupation_hisco": None,
            "origin": i["bruid_herkomst"],
            "homeLocation": i["bruid_adres"],
            "parents_deceased": True if i["bruid_ouders_overleden"] == 1 else False,
            "marital_status_modern": i["Bride_marital-status"],
            "signature": True if i["bruid_handtekening"] == 1 else False,
        }

        bride_witnesses = []
        for n, column in enumerate(
            [
                "bruid_getuige_1",
                "bruid_getuige_2",
                "bruid_getuige_3",
                "bruid_getuige_4",
            ],
            1,
        ):

            (
                givenName,
                patronym,
                surnamePrefix,
                baseSurname,
                literalName,
            ) = parsePersonName(i[column])

            relation = i[column.replace("_getuige_", "_getuige_relatie_")]
            if type(relation) == str and "Niet gespecificeerd" in relation:
                relation = None
            elif relation == "Anders":
                relation = i[f"bruid_getuige_relatie_{n}_anders"]

            if n == 1 and not i["bride_wn1_relation_standardized"].startswith("_"):
                relation_modern = i["bride_wn1_relation_standardized"]
            else:
                relation_modern = None

            witness_data = {
                "id": uri + "-bride-witness-" + str(n),
                "relation": relation,
                "relation_modern": relation_modern,
                "hasName": {
                    "givenName": givenName,
                    "patronym": patronym,
                    "surnamePrefix": surnamePrefix,
                    "baseSurname": baseSurname,
                    "literalName": literalName,
                },
            }
            if literalName:
                bride_witnesses.append(witness_data)

        bride["witnesses"] = bride_witnesses

        # ex_groom
        givenName, surnamePrefix, baseSurname, literalName = parseInversePersonName(
            i["bruid_ex"]
        )

        bride_ex = {
            "id": uri + "-bride-ex",
            "hasName": {
                "givenName": givenName,
                "surnamePrefix": surnamePrefix,
                "baseSurname": baseSurname,
                "literalName": literalName,
            },
        }
        if literalName:
            bride["exHusband"] = bride_ex
        else:
            bride["exHusband"] = None

        for k, v in bride.items():
            if type(v) == str and v.startswith(("_", "{")):
                bride[k] = None

        d["bride"] = bride

        data.append(d)

    with open("jiw_ga.json", "w") as outfile:
        json.dump(data, outfile, indent=4)

    df.to_csv("JIW_GA.csv", index=False)
