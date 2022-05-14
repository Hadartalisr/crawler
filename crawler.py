from urllib.parse import unquote
import requests
import lxml.html
import logging
import json
import re
import rdflib


logging.basicConfig(level=logging.ERROR)

WIKI_PREFIX = "http://en.wikipedia.org"
ROOT_SUFFIX = "/wiki/List_of_countries_by_population_(United_Nations)"
CAPITAL = 'capital'
GOVERNMENT = 'government'
AREA = 'area'
POPULATION = 'population'
PRESIDENT = 'president'
COUNTRY_KEYS = [CAPITAL, GOVERNMENT, AREA, POPULATION, PRESIDENT]
NAME = 'name'
WHEN_BORN = 'when_born'
WHERE_BORN = 'where_born'
PRESIDENT_KEYS = [NAME, WHEN_BORN, WHERE_BORN]


def get_url(suffix):
    return f"{WIKI_PREFIX}{suffix}"


def unquote_u(source):
    result = source
    if '%u' in result:
        result = result.replace('%u', '\\u').decode('unicode_escape')
    result = unquote(result)
    return result


def get_entity(suffix):
    return rdflib.URIRef(get_url(unquote_u(suffix)))


g = rdflib.Graph()

population_rel = get_entity("/wiki/Population")
capital_city = get_entity("/wiki/Capital_city")
government_form = get_entity("/wiki/Government")
area_rel = get_entity("/wiki/Area")
president_rel = get_entity("/wiki/President_(government_title)")
prime_minister_rel = get_entity("/wiki/Prime_minister")
place_of_birth = get_entity("/wiki/Place_of_birth")
date_of_birth = get_entity("/wiki/Birthday")

COUNTRIES_TO_CRAWL = 4


def index(countries):
    for country in countries:
        country_entity = get_entity(country['name'])
        if CAPITAL in country.keys():
            for capital in country[CAPITAL]:
                capital_entity = get_entity(capital)
                g.add((capital_entity, capital_city, country_entity))
        if GOVERNMENT in country.keys():
            for government in country[GOVERNMENT]:
                government_entity = get_entity(government)
                g.add((government_entity, government_form, country_entity))
        # if AREA in country.keys():
        #     area_entity = rdflib.term.Node(country[AREA]) #TODO fake a url
        #     g.add((area_entity, area_rel, country_entity))
        # if POPULATION in country.keys():
        #     population_entity = rdflib.term.Node(country[POPULATION])
        #     g.add((population_entity, population_rel, country_entity))
        if PRESIDENT in country.keys():
            president = country[PRESIDENT]
            if NAME in president.keys():
                president_entity = get_entity(president[NAME])
                g.add((president_entity, president_rel, country_entity))
                if WHEN_BORN in president.keys():
                    when_born_entity = get_entity(president[WHEN_BORN])
                    g.add((when_born_entity, date_of_birth, president_entity))
                if WHERE_BORN in president.keys():
                    where_born_entity = get_entity(president[WHERE_BORN])
                    g.add((where_born_entity, place_of_birth, president_entity))

    g.serialize("graph.nt", format="nt")


def crawl():
    countries = get_countries()
    i = 0
    for country in countries:
        crawl_country(country)
        check_country(country)
        i += 1
        if i > COUNTRIES_TO_CRAWL:
            break
    print(json.dumps(countries, indent=4))
    return countries


def check_country(country):
    for key in COUNTRY_KEYS:
        if key not in country.keys():
            logging.error(f"{key} is not a key")
            continue
        if country[key] is None:
            logging.error("country[key] is None")


def crawl_country(country):
    res = requests.get(get_url(country['name']))
    doc = lxml.html.fromstring(res.content)
    infobox = doc.xpath("//table[contains(@class,'infobox')]")[0]
    country[CAPITAL] = get_country_capital(infobox)
    country[GOVERNMENT] = get_country_government(infobox)
    country[AREA] = get_country_area(infobox)
    country[POPULATION] = get_country_population(infobox)
    country[PRESIDENT] = get_country_president(infobox)


def get_country_capital(infobox):
    return infobox.xpath("//table//tr[.//th/text()='Capital']/td/a[@title]/@href")


def get_country_government(infobox):
    return infobox.xpath("//table//tr[.//a/text()='Government']/td/a[@title]/@href")


def get_country_area(infobox):
    res = ""
    text = infobox.xpath("//table//tr[contains(th,'Total')]/td[contains(text(),'km')]/text()")
    string = align_string(''.join(text))
    match = re.search('([0-9,]+[^0-9]*km)', string)
    if match:
        res = match.group(0)
        return res
    text = infobox.xpath("//table//tr[contains(th,'Total')]/td/text()")
    string = align_string(''.join(text))
    match = re.search('([0-9,]+[^0-9]*km)', string)
    if match:
        res = match.group(0)
        return res
    text = infobox.xpath("//table//tr[contains(th,'Land')]/td/text()")
    string = align_string(''.join(text))
    match = re.search('([0-9,]+[^0-9]*km)', string)
    if match:
        res = match.group(0)
        return res
    return res


def get_country_population(infobox):
    res = ""
    text = infobox.xpath("//table//tr//a[contains(text(),'Population')]/ancestor::tr/following-sibling::tr[1]/td/text()")
    string = align_string(''.join(text))
    match = re.search('(\\d{1,3}(,\\d{3})+)', string)
    if match:
        res = match.group(0)
        return res
    match = re.search('(\\d{1,3}(.\\d{3})+)', string)
    if match:
        res = match.group(0)
        return res
    text = infobox.xpath("//table//tr//a[contains(.,'Population')]//ancestor::tr/following-sibling::tr[1]//text()")
    string = align_string(''.join(text))
    match = re.search('(\\d{1,3}(,\\d{3})+)', string)
    if match:
        res = match.group(0)
        return res
    match = re.search('(\\d{1,3}(.\\d{3})+)', string)
    if match:
        res = match.group(0)
        return res
    return res


def get_country_president(infobox):
    president = {}
    text = infobox.xpath("//table//tr//a[contains(.,'President')]/ancestor::th/following-sibling::td[1]/a/@href")
    if len(text) > 0:
        president[NAME] = text[0]
    if NAME not in president.keys():
        logging.error('not found president')
        return president
    crawl_president(president)
    return president


def crawl_president(president):
    doc = get_html(president[NAME])
    infobox = doc.xpath("//table[contains(@class,'infobox')]")[0]
    president[WHEN_BORN] = get_when_born(infobox)
    president[WHERE_BORN] = get_where_born(infobox)


def get_when_born(infobox):
    text = infobox.xpath("//table//tr[contains(.,'Born')]//span[contains(@class,'bday')]/text()")
    date = ""
    if len(text) > 0:
        # date returned will be a datetime.datetime object. here we are only using the first match.
        return text[0]
    return date


def get_where_born(infobox):
    text = infobox.xpath("//table//tr[contains(.,'Born')]//a[contains(@href,'wiki')]/@href")
    place = ""
    if 0 < len(text) < 10:
        return text[len(text)-1]
    if len(text) > 0: #TODO handle
        return text[0]
    return place


def get_countries():
    doc = get_html(ROOT_SUFFIX)
    table_countries = doc.xpath('//*[@id="mw-content-text"]/div[1]/table/tbody/tr/td[1]//a[@title]')
    countries = []
    for country in table_countries:
        countries.append({
            'name': country.attrib.get('href')
        })
    return countries


def align_string(string):
    res = string.replace(u'\xa0', u' ')
    return res


def get_html(suffix):
    res = requests.get(get_url(suffix))
    doc = lxml.html.fromstring(res.content)
    return doc


countries = crawl()
index(countries)

# country = {'name': '/wiki/Russia'}
# crawl_country(country)
# print(json.dumps(country, indent=4))