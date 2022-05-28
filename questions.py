import rdflib
import crawler
import re
import pandas as pd
import openpyxl


def get_entity_url(entity: str):
    entity = entity.replace(" ", "_")
    return "http://en.wikipedia.org/wiki/{entity}".format(entity=entity)


# Who is the president of <country>?
def get_q1(country_name):
    country = get_entity_url(country_name)
    q1 = "select ?p where {{" \
         " ?p <{rel}> <{entity}> ." \
         "}}".format(rel=crawler.president_url, entity=country)
    return q1


# Who is the prime minister of <country>?
def get_q2(country_name):
    country = get_entity_url(country_name)
    q1 = "select ?p where {{" \
         " ?p <{rel}> <{entity}> ." \
         "}}".format(rel=crawler.prime_minister_url, entity=country)
    return q1


# What is the population of <country>?
def get_q3(country_name):
    country = get_entity_url(country_name)
    q1 = "select ?p where {{" \
         " ?p <{rel}> <{entity}> ." \
         "}}".format(rel=crawler.population_url, entity=country)
    return q1


# What is the area of <country>?
def get_q4(country_name):
    country = get_entity_url(country_name)
    q1 = "select ?p where {{" \
         " ?p <{rel}> <{entity}> ." \
         "}}".format(rel=crawler.area_url, entity=country)
    return q1


# What is the form of government in <country>?
def get_q5(country_name):
    country = get_entity_url(country_name)
    q1 = "select ?p where {{" \
         " ?p <{rel}> <{entity}> ." \
         "}}".format(rel=crawler.government_form_url, entity=country)
    return q1


# What is the capital of <country>?
def get_q6(country_name):
    country = get_entity_url(country_name)
    q1 = "select ?p where {{" \
         " ?p <{rel}> <{entity}> ." \
         "}}".format(rel=crawler.capital_city_url, entity=country)
    return q1


# When was the president of <country> born?
def get_q7(country_name):
    country = get_entity_url(country_name)
    q1 = "select ?w where {{" \
         " ?p <{relA}> <{entity}> ." \
         " ?w <{relB}> ?p ." \
         "}}".format(relA=crawler.president_rel, entity=country, relB=crawler.date_of_birth)
    return q1


# Where was the president of <country> born?
def get_q8(country_name):
    country = get_entity_url(country_name)
    q1 = "select ?w where {{" \
         " ?p <{relA}> <{entity}> ." \
         " ?w <{relB}> ?p ." \
         "}}".format(relA=crawler.president_rel, entity=country, relB=crawler.place_of_birth)
    return q1


# When was the prime minister of <country> born?
def get_q9(country_name):
    country = get_entity_url(country_name)
    q1 = "select ?w where {{" \
         " ?p <{relA}> <{entity}> ." \
         " ?w <{relB}> ?p ." \
         "}}".format(relA=crawler.prime_minister_rel, entity=country, relB=crawler.date_of_birth)
    return q1


# Where was the prime minister of <country> born?
def get_q10(country_name):
    country = get_entity_url(country_name)
    q1 = "select ?w where {{" \
         " ?p <{relA}> <{entity}> ." \
         " ?w <{relB}> ?p ." \
         "}}".format(relA=crawler.prime_minister_rel, entity=country, relB=crawler.place_of_birth)
    return q1


# Who is <entity>?
def who_is(person_name):
    g1 = rdflib.Graph()
    g1.parse("graph.nt", format="nt")
    person = get_entity_url(person_name)
    query = "select ?r ?c where {{" \
            " <{person}> ?r ?c ." \
            "}}".format(person=person)
    res = g1.query(query)
    arr = []
    for result in res:
        rel = extract_result(result[0].n3())
        country = extract_result(result[1].n3())
        arr.append("{rel} of {country}".format(rel=rel, country=country))
    return arr


# How many <government_form1> are also <government_form2>?
def get_q12(government_form_a: str, government_form_b: str):
    g1 = rdflib.Graph()
    g1.parse("graph.nt", format="nt")
    government_form_a = get_entity_url(government_form_a.capitalize())
    government_form_b = get_entity_url(government_form_b.capitalize())
    q1 = "select (count(distinct ?c) as ?count) where {{" \
         " <{entityA}> <{rel}> ?c ." \
         " <{entityB}> <{rel}> ?c ." \
         "}}".format(rel=crawler.government_form, entityA=government_form_a, entityB=government_form_b)
    res = g1.query(q1)
    for result in res:
        return [result.asdict()['count'].toPython()]


# List all countries whose capital name contains the string <str>
def get_q13(substr):
    q1 = "select ?country where {{" \
         " ?capital <{relA}> ?country " \
         " filter( regex(str(?capital), \"{str}\")) " \
         "}}".format(relA=crawler.capital_city, str=substr)
    return q1


# How many presidents were born in <country>?
def get_q14(country):
    g1 = rdflib.Graph()
    g1.parse("graph.nt", format="nt")
    country_entity = get_entity_url(country)
    q1 = "select (count(distinct ?president) as ?count) where {{" \
         " <{entityA}> <{rel}> ?president ." \
         " ?president <{relB}> ?any ." \
         "}}".format(rel=crawler.place_of_birth, entityA=country_entity, relB=crawler.president_rel)
    res = g1.query(q1)
    for result in res:
        return [result.asdict()['count'].toPython()]


def extract_result(str):
    return str.replace("<http://en.wikipedia.org/wiki/", "").replace("_", " ").replace(">", "")


def handle_basic_question(query):
    g1 = rdflib.Graph()
    g1.parse("graph.nt", format="nt")
    res = g1.query(query)
    arr = []
    for result in res:
        str = result[0].n3()
        arr.append(extract_result(str))
    return arr


def get_question(user_question):
    regex_1 = "Who is the president of ([a-z A-z]+)?"
    m = re.match(regex_1, user_question)
    if m:
        country_name = m.group(1)
        query = get_q1(country_name)
        return handle_basic_question(query)

    regex_2 = "Who is the prime minister of ([a-z A-z]+)?"
    m = re.match(regex_2, user_question)
    if m:
        country_name = m.group(1)
        query = get_q2(country_name)
        return handle_basic_question(query)

    regex_3 = "What is the population of ([a-z A-z]+)?"
    m = re.match(regex_3, user_question)
    if m:
        country_name = m.group(1)
        query = get_q3(country_name)
        return handle_basic_question(query)

    regex_4 = "What is the area of ([a-z A-z]+)?"
    m = re.match(regex_4, user_question)
    if m:
        country_name = m.group(1)
        query = get_q4(country_name)
        return handle_basic_question(query)

    regex_5 = "What is the form of government in ([a-z A-z]+)?"
    m = re.match(regex_5, user_question)
    if m:
        country_name = m.group(1)
        query = get_q5(country_name)
        return handle_basic_question(query)

    regex_6 = "What is the capital of ([a-z A-z]+)?"
    m = re.match(regex_6, user_question)
    if m:
        country_name = m.group(1)
        query = get_q6(country_name)
        return handle_basic_question(query)

    regex_7 = "When was the president of ([a-z A-z]+) born?"
    m = re.match(regex_7, user_question)
    if m:
        country_name = m.group(1)
        query = get_q7(country_name)
        return handle_basic_question(query)

    regex_8 = "Where was the president of ([a-z A-z]+) born?"
    m = re.match(regex_8, user_question)
    if m:
        country_name = m.group(1)
        query = get_q8(country_name)
        return handle_basic_question(query)

    regex_9 = "When was the prime minister of ([a-z A-z]+) born?"
    m = re.match(regex_9, user_question)
    if m:
        country_name = m.group(1)
        query = get_q9(country_name)
        return handle_basic_question(query)

    regex_10 = "Where was the prime minister of ([a-z A-z]+) born?"
    m = re.match(regex_10, user_question)
    if m:
        country_name = m.group(1)
        query = get_q10(country_name)
        return handle_basic_question(query)

    regex_11 = "Who is ([a-z A-z]+)?"
    m = re.match(regex_11, user_question)
    if m:
        person = m.group(1)
        return who_is(person)

    regex_12 = "How many ([a-z A-z]+) are also ([a-z A-z]+)?"
    m = re.match(regex_12, user_question)
    if m:
        government_form_a = m.group(1)
        government_form_b = m.group(2)
        return get_q12(government_form_a, government_form_b)

    regex_13 = "List all countries whose capital name contains the string ([a-z A-z]+)"
    m = re.match(regex_13, user_question)
    if m:
        str = m.group(1)
        query = get_q13(str)
        return handle_basic_question(query)


    regex_14 = "Where was the president of ([a-z A-z]+) born?"
    m = re.match(regex_14, user_question)
    if m:
        country = m.group(1)
        return get_q14(country)


simple_questions = [
    "Who is the president of <country>?",
    "Who is the prime minister of <country>?",
    "What is the population of <country>?",
    "What is the area of <country>?",
    "What is the form of government in <country>?",
    "What is the capital of <country>?",
    "When was the president of <country> born?",
    "Where was the president of <country> born?",
    "When was the prime minister of <country> born?",
    "Where was the prime minister of <country> born?",
]

other_questions = [
    "Who is <entity>?",
    "How many <government_form1> are also <government_form2>?",
    "List all countries whose capital name contains the string <str>",
    # "How many presidents were born in <country>? "
]


def main():
    # for q in simple_questions:
    #     for c in ['India', 'Mexico', 'Japan', 'Russia', 'Germany', 'Brazil', 'Pakistan', 'Nigeria', 'Philippines', 'Philippines', 'Democratic Republic of the Congo', 'Ethiopia', 'Vietnam', 'Bangladesh', 'Egypt', 'United Kingdom', 'Thailand', 'Turkey', 'Iran', 'China', 'United States', 'Indonesia']:
    #         q_a = q.replace("<country>", c)
    #         res = get_question(q_a)
    #         print(res)
    #     print("------\n\n")
    # q = "Who is <entity>?".replace("<entity>", "Xi Jinping")
    # print(get_question(q))
    # q = "Who is <entity>?".replace("<entity>", "Narendra Modi")
    # print(get_question(q))
    #
    # q = "How many federalism are also republic?"
    # print(get_question(q))
    #
    # q = "List all countries whose capital name contains the string i"
    # print(get_question(q))
    #
    # q = "How many presidents were born in India?"
    # print(get_question(q))
    test()


def test():
    xl = pd.ExcelFile("qa.xlsx")
    df = xl.parse("Sheet1")
    for index, row in df.iterrows():
        q = row['q']
        a = row['a']
        our_answer = get_question(q)
        print(f"{q} \n real answer: {a}\n our answer: {our_answer}")

main()

# g1 = rdflib.Graph()
# g1.parse("graph.nt", format="nt")
#
# x1 = g1.query(q1)
# for result in x1:
#     print(result)

