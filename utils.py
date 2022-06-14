import pymongo.database
from pymongo import MongoClient
from dotenv import load_dotenv
from newspaper import Article
from pprint import pprint
import os
import newspaper
import en_core_web_lg

# Load .env
load_dotenv()

# Load the environment variables
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
API_KEY = os.getenv('API_KEY')

# The mongoDB connection string
CONNECTION_STRING = f'mongodb+srv://{USER}:{PASSWORD}@cluster0.rjiqa.mongodb.net/?retryWrites=true&w=majority'


def get_database() -> pymongo.database.Database:
    """This function retrieves the mongoDB Atlas database.

    :return: The database.
    """

    # Create a connection using MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Get ARLIS database
    db = client['ARLIS']

    return db


def get_collection(database: pymongo.database.Database = None, date: str = None,
                   technology: str = None) -> (pymongo.cursor.Cursor, int):
    """This function retrieves the collection from mongoDB Atlas database based on date and technology.

    :param database: The mongoDB Atlas database.
    :param date: The date.
    :param technology: The technology.
    :return: The articles mongoDB Atlas collection.
    """

    # Convert datetime object to date string
    date_string = date.strftime('%Y%m%d')

    # Make technology lowercase
    technology = technology.lower()

    # Replace spaces with underscore
    technology = technology.replace(' ', '_')

    # The collection name
    collection_name = f'{date_string}_{technology}'

    # Get collection
    collection = database[collection_name].find()

    # Get collection count
    collection_count = database[collection_name].count_documents({})

    return collection, collection_count


def dictionary_to_list(dictionary: dict = None) -> list:
    """This function converts the dictionary of companies to a list of companies.

    :param dictionary: The dictionary.
    :return: A list.
    """

    # The companies list
    companies_list = []

    # Loop through companies dictionary and convert it to list to add to database
    for k, v in dictionary.items():
        companies_list.append({'Name': k, 'Count': v['Count']})

    return companies_list


def store_documents(database: pymongo.database.Database = None, document: dict = None, date: str = None,
                    technology: str = None) -> None:
    """This function inserts a prediction as a document in mongoDB Atlas database.

    :param database: The mongoDB Atlas database.
    :param document: The document.
    :param date: The date.
    :param technology: The technology.
    """

    # Convert datetime object to date string
    date_string = date.strftime('%Y%m%d')

    # Make technology lowercase
    technology = technology.lower()

    # Replace spaces with underscore
    technology = technology.replace(' ', '_')

    # The collection name
    collection_name = f'{date_string}_{technology}_prediction'

    # Get collection
    collection = database[collection_name]

    # Insert document
    collection.insert_many(documents=document)


def get_article_text(url: str = None) -> str:
    """This function gets the article text.

    :param url: The article url.
    :return: The article text.
    """

    # Get article
    article = Article(url)

    # Download article
    article.download()

    # Parse article
    article.parse()

    # Get text
    text = article.text

    return text


def count_companies(companies: dict = None, text: str = None) -> dict:
    """This function counts the number of time a company appears in an article using Name Entity Recognition.

    :param companies: The dictionary of companies.
    :param text: The article text.
    :return: The companies stored in a dictionary with counts.
    """

    # The NLP
    nlp = en_core_web_lg.load()

    # Do Name Entity Recognition (NER) on the article text
    doc = nlp(text)

    # Count the number of company appearances in articles
    for word in doc.ents:
        # If word is a company, add to companies dictionary
        if word.label_ == 'ORG':
            # Convert word to string
            word = str(word)

            # Add word to companies dictionary
            companies.setdefault(word, {}).setdefault('Count', 0)
            companies[word]['Count'] += 1

    return companies


# TODO return
def natural_language_processing(articles: pymongo.cursor.Cursor = None) -> dict:
    # The companies list
    companies = {}

    # TODO testing
    articles = articles[:1]

    for article in articles:
        # Get url
        url = article['link']

        # Get article text
        try:
            text = get_article_text(url)
        except newspaper.article.ArticleException:
            continue

        # Clean text
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('\xa0', ' ')

        # Count the number of times a company appears in an article
        companies = count_companies(
            companies=companies,
            text=text
        )

    return companies
