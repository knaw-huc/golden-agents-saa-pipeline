import os
import xmltodict

from datetime import datetime, timedelta
from dateutil import parser

from dataclasses import dataclass


@dataclass
class EAD:
    id: str
    title: str
    author: str
    publisher: str

    collection: list


@dataclass
class Collection:

    id: str
    name: str
    description: str
    identifier: str
    date: str
    language: str
    repository: str
    origination: str
    # collectionCorporation: str

    children: list


@dataclass(order=True)
class C:
    id: str
    name: str
    description: str
    identifier: str
    date: str

    children: list
    parent: Collection

    scans: list

    level: str


def parseEAD(xmlfile):
    with open(xmlfile, 'rb') as xmlrbfile:
        parse = xmltodict.parse(xmlrbfile,
                                force_list={'note', 'c'},
                                dict_constructor=dict)
        ead = parse['ead']

    head = ead['eadheader']

    ead = EAD(id=head['eadid']['@identifier'],
              title=head['filedesc']['titlestmt']['titleproper'],
              author=head['filedesc']['titlestmt'].get('author', ''),
              publisher=head['filedesc']['publicationstmt']['publisher'],
              collection=[parseCollection(ead)])

    return ead


def parseDsc(serie, parentCollection=None):

    did = serie['did']

    id = did['unitid']['@identifier']
    code = did['unitid']['#text']
    date = did.get('unitdate')

    if date:
        date = parseDate(date['@normal'])
    else:
        date = dict()

    name = did.get('unittitle', "")
    if '#text' in name:
        name = name['#text']

    comment = ""
    scans = []

    if serie['@level'] == 'file':  # reached the end!
        if 'note' in did:
            for note in did['note']:
                if note['@label'] == "NB":
                    comment = note['p']
                elif note['@label'] == "ImageId":
                    scans = note['p'].split(' \n')

        return C(id=id,
                 name=name,
                 description=comment,
                 identifier=code,
                 date=date,
                 children=[],
                 parent=parentCollection,
                 scans=scans,
                 level=serie['@level'])

    else:
        children = []
        for k in serie:
            if k not in ['head', '@level', 'did']:
                for subelement in serie[k]:
                    if type(subelement) != str:
                        children.append(
                            parseDsc(subelement,
                                     parentCollection=parentCollection))

        return C(id=id,
                 name=name,
                 description=comment,
                 identifier=code,
                 date=date,
                 children=children,
                 parent=parentCollection,
                 scans=scans,
                 level=serie['@level'])


def parseCollection(ead):

    archdesc = ead['archdesc']

    collection = Collection(
        id=archdesc['did']['unitid']['@identifier'],
        name=archdesc['did']['unittitle']['#text'],
        description=archdesc['did']['abstract']['#text']
        if archdesc['did'].get('abstract') else "",
        identifier=archdesc['did']['unitid']['#text'],
        date=parseDate(archdesc['did']['unitdate'].get('@normal')),
        language=archdesc['did']['langmaterial'],
        repository=archdesc['did']['repository']['corpname'],
        origination=archdesc['did']['origination'],
        children=[]
        # collectionCorporation=archdesc['did']['origination']['corpname'],
    )

    collection.children = [
        parseDsc(serie, parentCollection=collection)
        for serie in archdesc['dsc']['c']
    ]

    return collection


def parseDate(date,
              circa=None,
              default=None,
              defaultBegin=datetime(2100, 1, 1),
              defaultEnd=datetime(2100, 12, 31)):

    if date is None or date == 's.d.':
        return {}

    date = date.strip()

    if '/' in date:
        begin, end = date.split('/')

        begin = parseDate(begin, default=defaultBegin)
        end = parseDate(end, default=defaultEnd)
    elif date.count('-') == 1:
        begin, end = date.split('-')

        begin = parseDate(begin, default=defaultBegin)
        end = parseDate(end, default=defaultEnd)
    elif 'ca.' in date:
        date, _ = date.split('ca.')

        begin = parseDate(date, default=defaultBegin, circa=365)
        end = parseDate(date, default=defaultEnd, circa=365)

    else:  # exact date ?

        if circa:
            begin = parser.parse(date, default=defaultBegin) - timedelta(circa)
            end = parser.parse(date, default=defaultEnd) + timedelta(circa)
        elif len(date) == 4:  # year only
            begin = (datetime(int(date), 1, 1), None)
            end = (None, datetime(int(date), 12, 31))
        else:
            begin = parser.parse(date, default=defaultBegin)
            end = parser.parse(date, default=defaultEnd)

    # And now some sem magic

    if begin == end:
        timeStamp = begin
    else:
        timeStamp = None

    if type(begin) == tuple:
        earliestBeginTimeStamp = begin[0].date() if begin[0] else None
        latestBeginTimeStamp = begin[1].date() if begin[1] else None
        beginTimeStamp = None
        timeStamp = None
    else:
        earliestBeginTimeStamp = begin.date()
        latestBeginTimeStamp = begin.date()
        beginTimeStamp = begin.date()

    if type(end) == tuple:
        earliestEndTimeStamp = end[0].date() if end[0] else None
        latestEndTimeStamp = end[1].date() if end[1] else None
        endTimeStamp = None
    else:
        earliestEndTimeStamp = end.date()
        latestEndTimeStamp = end.date()
        endTimeStamp = end.date()

    if default:
        if type(begin) == tuple:
            begin = min([i for i in begin if i])
        if type(end) == tuple:
            end = max([i for i in end if i])
        return begin, end

    temporal = f"{earliestBeginTimeStamp or '..'}/{latestEndTimeStamp or '..'}"

    dt = {
        "temporal": temporal,
        "hasTimeStamp": timeStamp,
        "hasBeginTimeStamp": beginTimeStamp,
        "hasEarliestBeginTimeStamp": earliestBeginTimeStamp,
        "hasLatestBeginTimeStamp": latestBeginTimeStamp,
        "hasEndTimeStamp": endTimeStamp,
        "hasEarliestEndTimeStamp": earliestEndTimeStamp,
        "hasLatestEndTimeStamp": latestEndTimeStamp
    }

    return dt


if __name__ == '__main__':
    # arguments = docopt(__doc__)
    # if arguments['convert'] and os.path.isfile(arguments['<xmlfile>']):

    #     print(f"Parsing {arguments['<xmlfile>']}")

    #     parseEAD(xmlfile=arguments['<xmlfile>'])

    import json

    for f in os.listdir('/home/leon/Documents/Golden_Agents/saaA2A/data/ead/'):

        if '5075' not in f:
            continue

        print(f)
        ead = parseEAD(
            os.path.join('/home/leon/Documents/Golden_Agents/saaA2A/data/ead/',
                         f))

        data = dict()

        for c in ead.children:
            data[c.code] = {
                'notaris': c.title,
                'code': c.code,
                'uri': f"https://archief.amsterdam/inventarissen/file/{c.id}",
                'inventories': dict()
            }

            codes = []
            inventories = []

            if getattr(c, 'children'):
                for c2 in c.children:
                    if not getattr(c2, 'children'):

                        inventories.append(
                            f"https://archief.amsterdam/inventarissen/file/{c2.id}"
                        )
                        codes.append(c2.code)
                    else:
                        for c3 in c2.children:
                            if not getattr(c3, 'children'):

                                inventories.append(
                                    f"https://archief.amsterdam/inventarissen/file/{c3.id}"
                                )
                                codes.append(c3.code)
                            else:
                                for c4 in c3.children:
                                    if not getattr(c4, 'children'):

                                        inventories.append(
                                            f"https://archief.amsterdam/inventarissen/file/{c4.id}"
                                        )
                                        codes.append(c4.code)

            data[c.code]['codes'] = codes
            data[c.code]['inventories'] = inventories

        with open('notarissenEAD.json', 'w') as outfile:
            json.dump(data, outfile)