import requests
import lxml.html
import logging
import json
import re

logging.basicConfig(level=logging.ERROR)

WIKI_PREFIX = "http://en.wikipedia.org"
ROOT_SUFFIX = "/wiki/List_of_countries_by_population_(United_Nations)"
CAPITAL = 'capital'
GOVERNMENT = 'government'
AREA = 'area'
POPULATION = 'population'
COUNTRY_KEYS = [CAPITAL, GOVERNMENT, AREA, POPULATION]

COUNTRIES_TO_CRAWL = 50


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


def get_url(suffix):
    return f"{WIKI_PREFIX}{suffix}"


crawl()

# country = {'name': '/wiki/Russia'}
# crawl_country(country)
# print(json.dumps(country, indent=4))