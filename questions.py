import rdflib
import crawler
import re


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
         " ?p <{rel}> <{entity}> ." \
         " ?p <{rel}> <{entity}> ." \
         "}}".format(rel=crawler.population_url, entity=country)
    return q1


#
# # What is the population of <country>?
# def get_q8(country_name):
#     country = get_entity_url(country_name)
#     q1 = "select ?p where {{" \
#          " ?p <{rel}> <{entity}> ." \
#          "}}".format(rel=crawler.population_url, entity=country)
#     return q1
#
#
# # What is the population of <country>?
# def get_q9(country_name):
#     country = get_entity_url(country_name)
#     q1 = "select ?p where {{" \
#          " ?p <{rel}> <{entity}> ." \
#          "}}".format(rel=crawler.population_url, entity=country)
#     return q1
#
#
# # What is the population of <country>?
# def get_q10(country_name):
#     country = get_entity_url(country_name)
#     q1 = "select ?p where {{" \
#          " ?p <{rel}> <{entity}> ." \
#          "}}".format(rel=crawler.population_url, entity=country)
#     return q1
#
#
# # What is the population of <country>?
# def get_q11(country_name):
#     country = get_entity_url(country_name)
#     q1 = "select ?p where {{" \
#          " ?p <{rel}> <{entity}> ." \
#          "}}".format(rel=crawler.population_url, entity=country)
#     return q1
#
# # What is the population of <country>?
# def get_q12(country_name):
#     country = get_entity_url(country_name)
#     q1 = "select ?p where {{" \
#          " ?p <{rel}> <{entity}> ." \
#          "}}".format(rel=crawler.population_url, entity=country)
#     return q1
#
# # What is the population of <country>?
# def get_q13(country_name):
#     country = get_entity_url(country_name)
#     q1 = "select ?p where {{" \
#          " ?p <{rel}> <{entity}> ." \
#          "}}".format(rel=crawler.population_url, entity=country)
#     return q1
#
# # What is the population of <country>?
# def get_q14(country_name):
#     country = get_entity_url(country_name)
#     q1 = "select ?p where {{" \
#          " ?p <{rel}> <{entity}> ." \
#          "}}".format(rel=crawler.population_url, entity=country)
#     return q1


def get_question(user_question):
    regex_1 = "Who is the president of ([a-z A-z]+)?"
    m = re.match(regex_1, user_question)
    if m:
        country_name = m.group(1)
        return get_q1(country_name)

    regex_2 = "Who is the prime minister of ([a-z A-z]+)?"
    m = re.match(regex_2, user_question)
    if m:
        country_name = m.group(1)
        return get_q2(country_name)

    regex_3 = "What is the population of ([a-z A-z]+)?"
    m = re.match(regex_3, user_question)
    if m:
        country_name = m.group(1)
        return get_q3(country_name)

    regex_4 = "What is the area of ([a-z A-z]+)?"
    m = re.match(regex_4, user_question)
    if m:
        country_name = m.group(1)
        return get_q4(country_name)

    regex_5 = "What is the form of government in ([a-z A-z]+)?"
    m = re.match(regex_5, user_question)
    if m:
        country_name = m.group(1)
        return get_q5(country_name)

    regex_6 = "What is the capital of ([a-z A-z]+)?"
    m = re.match(regex_6, user_question)
    if m:
        country_name = m.group(1)
        return get_q6(country_name)

    regex_7 = "When was the president of ([a-z A-z]+) born?"
    m = re.match(regex_7, user_question)
    if m:
        country_name = m.group(1)
        return get_q7(country_name)

    # regex_8 = "Where was the president of <country> born?"
    # m = re.match(regex_3, user_question)
    # if m:
    #     country_name = m.group(1)
    #     return get_q3(country_name)
    #
    # regex_9 = "Where was the president of <country> born?"
    # m = re.match(regex_3, user_question)
    # if m:
    #     country_name = m.group(1)
    #     return get_q3(country_name)
    #
    # regex_10 = "Where was the president of <country> born?"
    # m = re.match(regex_3, user_question)
    # if m:
    #     country_name = m.group(1)
    #     return get_q3(country_name)
    #
    #
    # regex_11 = "Where was the president of <country> born?"
    # m = re.match(regex_3, user_question)
    # if m:
    #     country_name = m.group(1)
    #     return get_q3(country_name)
    #
    #
    # regex_12 = "Where was the president of <country> born?"
    # m = re.match(regex_3, user_question)
    # if m:
    #     country_name = m.group(1)
    #     return get_q3(country_name)
    #
    #
    # regex_13 = "Where was the president of <country> born?"
    # m = re.match(regex_3, user_question)
    # if m:
    #     country_name = m.group(1)
    #     return get_q3(country_name)
    #
    #
    # regex_14 = "Where was the president of <country> born?"
    # m = re.match(regex_3, user_question)
    # if m:
    #     country_name = m.group(1)
    #     return get_q3(country_name)


questions = [
    "Who is the president of <country>?",
    "Who is the prime minister of <country>?",
    "What is the population of <country>?",
    "What is the area of <country>?",
    "What is the form of government in <country>?",
    "What is the capital of <country>?",
    "When was the president of <country> born?",
    # "Where was the president of <country> born?",
    # "When was the prime minister of <country> born?",
    # "Where was the prime minister of <country> born?",
    # "Who is <entity>?",
    # "How many <government_form1> are also <government_form2>?",
    # "List all countries whose capital name contains the string <str>",
    # "How many presidents were born in <country>? "
]


def main():
    g1 = rdflib.Graph()
    g1.parse("graph.nt", format="nt")
    for q in questions:
        q = q.replace("<country>", "India")
        sparql = get_question(q)
        print(sparql)
        x1 = g1.query(sparql)
        for result in x1:
            print(result)


main()

# g1 = rdflib.Graph()
# g1.parse("graph.nt", format="nt")
#
# x1 = g1.query(q1)
# for result in x1:
#     print(result)
