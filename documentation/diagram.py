from diagrams import Diagram
from diagrams.custom import Custom
from diagrams.programming.language import Python
from diagrams.onprem.database import MongoDB
from diagrams.onprem.client import Users
import os

# Set Graphviz PATH
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'

with Diagram(name='Team AL - Predictive Analysis Design Document', filename='Application Programming Interface', direction='LR'):
    # Initialize icons
    newscatcherapi = Custom('newscatcherapi\n(api)', './my_resources/newscatcherapi.png')
    python = Python('python\n(programming language)')
    mongodb1 = MongoDB('mongodb\n(database)')
    mongodb2 = MongoDB('mongodb\n(database)')
    spacy = Custom('spaCy\n(machine learning)', './my_resources/spacy.png')
    nltk = Custom('nltk\n(machine learning)', './my_resources/nltk.png')
    streamlit = Custom('streamlit\n(web app)', './my_resources/streamlit.png')
    users = Users('analysts\n(users)')

    python >> newscatcherapi >> mongodb1 >> spacy >> nltk >> mongodb2 >> streamlit >> users
