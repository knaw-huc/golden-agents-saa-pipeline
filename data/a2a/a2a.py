import os
from sickle import Sickle
from sickle.iterator import OAIResponseIterator


def main(url: str):
    for (setSpec, name) in [
        ("08953f2f-309c-baf9-e5b1-0cefe3891b37",
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
         "SAA-ID-007_SAA_Index_op_boetes_op_trouwen_en_begraven"),
        ("9823b7a8-ab79-a098-4ab0-26e799ea5659",
         "SAA-ID-008_SAA_Index_op_begraafregisters_voor_1811"),
        ("8137be5e-1977-9c2b-1ead-b031fe39ed1e",
         "SAA-ID-009_SAA_Index_op_overledenen_gast_pest_werk_spinhuis"),
        ("760c1b75-122c-8965-170a-9b6701184533",
         "SAA-ID-010_SAA_Index_op_averijgrossen"),
        ("d5e8b387-d8f9-8a8b-dd17-00f7b6761553",
         "SAA-ID-011_SAA_Index_op_boedelpapieren"),
        ("3349cddf-c176-75e8-005f-705dbca96c4f",
         "SAA-ID-012_SAA_Index_op_lidmatenregister_doopsgezinde_gemeente")
    ]:

        if os.path.exists(name):
            continue
        os.makedirs(name)

        sickleIt = Sickle(url,
                          iterator=OAIResponseIterator,
                          max_retries=200,
                          timeout=300,
                          retry_status_codes=[502, 503])
        responses = sickleIt.ListRecords(metadataPrefix='oai_a2a', set=setSpec)

        for n, i in enumerate(responses, 1):
            print(n)
            with open(os.path.join(name,
                                   str(n).zfill(9) + '.xml'), 'wb') as outfile:
                outfile.write(i.raw.encode('utf8').strip())

if __name__ == "__main__":
    main(
        url=
        "https://webservices.picturae.com/a2a/a66155dd-f750-40be-9ddd-244d72248fa3"
    )
