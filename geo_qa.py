import crawler
import questions
import sys


def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == "create":
            countries = crawler.crawl()
            crawler.index(countries)
    if len(sys.argv) == 3:
        if sys.argv[1] == "question":
            print(questions.answer_question(sys.argv[2]))


if __name__ == '__main__':
    main()
