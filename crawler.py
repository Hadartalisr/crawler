from urllib.parse import unquote
from urllib.parse import quote
from rdflib.namespace import XSD
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
PRIME_MINISTER = 'prime_minister'
COUNTRY_KEYS = [CAPITAL, GOVERNMENT, AREA, POPULATION, PRESIDENT, PRIME_MINISTER]
NAME = 'name'
WHEN_BORN = 'when_born'
WHERE_BORN = 'where_born'
PRESIDENT_KEYS = [NAME, WHEN_BORN, WHERE_BORN]
PRIME_MINISTER_KEYS = [NAME, WHEN_BORN, WHERE_BORN]


def get_url(suffix):
    return f"{WIKI_PREFIX}{suffix}".replace(" ", "_")


def unquote_u(source):
    result = source
    if '%u' in result:
        result = result.replace('%u', '\\u').decode('unicode_escape')
    result = unquote(result)
    if '/' in result:
        i = result.rindex('/')
        result = result[:i]+quote(result[i:])
    return result


def get_entity(suffix):
    return rdflib.URIRef(get_url(unquote_u(suffix)))


g = rdflib.Graph()

population_url = get_url("/wiki/Population")
capital_city_url = get_url("/wiki/Capital_city")
government_form_url = get_url("/wiki/Government")
area_url = get_url("/wiki/Area")
president_url = get_url("/wiki/President")
prime_minister_url = get_url("/wiki/Prime_minister")
place_of_birth_url = get_url("/wiki/Place_of_birth")
date_of_birth_url = get_url("/wiki/Birthday")

population_rel = get_entity("/wiki/Population")
capital_city = get_entity("/wiki/Capital_city")
government_form = get_entity("/wiki/Government")
area_rel = get_entity("/wiki/Area")
president_rel = get_entity("/wiki/President")
prime_minister_rel = get_entity("/wiki/Prime_minister")
place_of_birth = get_entity("/wiki/Place_of_birth")
date_of_birth = get_entity("/wiki/Birthday")

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
        if AREA in country.keys():
            area_entity = get_entity(country[AREA])
            g.add((area_entity, area_rel, country_entity))
        if POPULATION in country.keys():
            population_entity = get_entity(country[POPULATION])
            g.add((population_entity, population_rel, country_entity))
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
        if PRIME_MINISTER in country.keys():
            prime_minister = country[PRIME_MINISTER]
            if NAME in prime_minister.keys():
                prime_minister_entity = get_entity(prime_minister[NAME])
                g.add((prime_minister_entity, prime_minister_rel, country_entity))
                if WHEN_BORN in prime_minister.keys():
                    when_born_entity = get_entity(prime_minister[WHEN_BORN])
                    g.add((when_born_entity, date_of_birth, prime_minister_entity))
                if WHERE_BORN in prime_minister.keys():
                    where_born_entity = get_entity(prime_minister[WHERE_BORN])
                    g.add((where_born_entity, place_of_birth, prime_minister_entity))
    g.serialize("ontology.nt", format="nt")


def crawl():
    countries = get_countries()
    for country in countries:
        crawl_country(country)
        check_country(country)
    return countries


def check_country(country):
    for key in COUNTRY_KEYS:
        if key not in country.keys():
            logging.error(f"{key} is not a key in {country[NAME]}")
            continue
        if country[key] is None:
            logging.error("country[key] is None")


def crawl_country(country):
    res = requests.get(get_url(country['name']))
    doc = lxml.html.fromstring(res.content)
    infobox = doc.xpath("//table[contains(@class,'infobox')]")
    if len(infobox) < 1:
        logging.error(f"didn't find infobox for {country[NAME]}")
        return country
    infobox = infobox[0]
    country[CAPITAL] = get_country_capital(infobox)
    country[GOVERNMENT] = get_country_government(infobox)

    area = get_country_area(infobox)
    a = re.match("[0-9,.]+", area)
    if a:
        txt = a.group(0).replace('.', ',') + " km squared"
        area = "/wiki/{area}".format(area=txt).replace(" ", "_")
        country[AREA] = area

    population = get_country_population(infobox)
    population = population.replace(".", ",")
    country[POPULATION] = "/wiki/{population}".format(population=population).replace(" ", "_")

    country[PRESIDENT] = get_country_president(infobox)
    country[PRIME_MINISTER] = get_country_prime_minister(infobox)


def get_country_capital(infobox):
    return infobox.xpath("(((//table)[contains(@class, 'infobox')]//tr)[.//text()='Capital']/td[1]//a)[@title][not(contains(@title, 'Geographic coordinate system'))]/@href")


def get_country_government(infobox):
    return infobox.xpath("(((//table)[contains(@class, 'infobox')]//tr)[.//text()='Government']/td[1]//a)[@title]/@href")


def get_country_area(infobox):
    res = ""
    text = infobox.xpath("//table//tr[contains(th,'Total')]/td[contains(text(),'km')]/text()")
    string = align_string(''.join(text))
    match = re.search('([0-9,.]+[^0-9]*km)', string)
    if match:
        res = match.group(0)
        return res
    text = infobox.xpath("//table//tr[contains(th,'Total')]/td/text()")
    string = align_string(''.join(text))
    match = re.search('([0-9,.]+[^0-9]*km)', string)
    if match:
        res = match.group(0)
        return res
    text = infobox.xpath("//table//tr[contains(th,'Land')]/td/text()")
    string = align_string(''.join(text))
    match = re.search('([0-9,.]+[^0-9]*km)', string)
    if match:
        res = match.group(0)
        return res
    return res


def get_country_population(infobox):
    res = ""
    text = infobox.xpath(
        "//table//tr//a[contains(text(),'Population')]/ancestor::tr/following-sibling::tr[1]/td/text()")
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
    text = infobox.xpath("//table//tr//a[. = 'President']/ancestor::th/following-sibling::td[1]//a/@href")
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


def get_country_prime_minister(infobox):
    prime_minister = {}
    text = infobox.xpath("//table//tr//a[contains(.,'Prime Minister')]/ancestor::th/following-sibling::td[1]/a/@href")
    if len(text) > 0:
        prime_minister[NAME] = text[0]
    if NAME not in prime_minister.keys():
        logging.error('not found prime minister')
        return prime_minister
    crawl_prime_minister(prime_minister)
    return prime_minister


def crawl_prime_minister(prime_minister):
    doc = get_html(prime_minister[NAME])
    infobox = doc.xpath("//table[contains(@class,'infobox')]")
    if len(infobox) > 0:
        infobox = infobox[0]
        prime_minister[WHEN_BORN] = get_when_born(infobox)
        prime_minister[WHERE_BORN] = get_where_born(infobox)
    else:
        logging.error("didn't find infobox for prime minister", prime_minister[NAME])


def get_when_born(infobox):
    def wb(infobox):
        text = infobox.xpath("//table//tr[contains(.,'Born')]//span[contains(@class,'bday')]/text()")
        date = ""
        if len(text) > 0:
            # date returned will be a datetime.datetime object. here we are only using the first match.
            return text[0]
        return date
    data = wb(infobox)
    return "/wiki/{data}".format(data=data).replace(" ", "_")


def get_where_born(infobox):
    all_countries = get_countries()
    td_links = infobox.xpath("(((//table)[contains(@class, 'infobox')]//tr)[contains(.,'Born')])//a[contains(@href,'wiki')]")
    td_text = infobox.xpath("(((//table)[contains(@class, 'infobox')]//tr)[contains(.,'Born')])/td/text()")
    place = ""
    for i in td_links:
        link = i.attrib.get('href')
        for country in all_countries:
            if country['name'] == link:
                return link
    for text in td_text:
        if text.startswith(', ') and len(text) > 2:
            text = text[2:]
        for country in all_countries:
            if country['name'][6:] == text:
                return country['name']
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


#countries = crawl()
#index(countries)

# country = {'name': '/wiki/Russia'}
# crawl_country(country)
# print(json.dumps(country, indent=4))
