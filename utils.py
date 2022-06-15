import pymongo.database
import newspaper
import en_core_web_lg
import streamlit as st
from pymongo import MongoClient
from newspaper import Article
from pprint import pprint
from datetime import date

# Load the environment variables
USER = st.secrets['USER']
PASSWORD = st.secrets['PASSWORD']
API_KEY = st.secrets['API_KEY']

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


def sidebar():
    """This function creates the sidebar.

    :return: The technology, date, and if submitted.
    """

    # Display form title
    st.sidebar.write('Predictive Analysis')

    # Sidebar select box to choose critical technology
    technology = st.sidebar.selectbox(
        label='Select a technology:',
        options=(
            '-',
            'Advanced Computing',
            'Advanced Engineering Materials',
            'Advanced Gas Turbine Engine Technologies',
            'Advanced Manufacturing',
            'Advanced Networked Sensing and Signature Management',
            'Advanced Nuclear Energy Technologies',
            'Artificial Intelligence',
            'Autonomous Systems and Robotics',
            'Biotechnologies',
            'Communication and Networking Technologies',
            'Directed Energy',
            'Financial Technologies',
            'Human-Machine Interfaces',
            'Hypersonics',
            'Networked Sensors and Sensing',
            'Quantum Information Technologies',
            'Renewable Energy Generation and Storage',
            'Semiconductors and Microelectronics',
            'Space Technologies and Systems'
        )
    )

    # Declare a form to handle a submit button
    with st.sidebar.form(key='my_form'):
        # Display select subfield depending on main technology
        match technology:
            case '-':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options='-'
                )
            case 'Advanced Computing':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Supercomputing',
                        'Edge computing',
                        'Cloud computing',
                        'Data storage',
                        'Computing architectures',
                        'Data processing and analysis techniques'
                    )
                )
            case 'Advanced Engineering Materials':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Materials by design and material genomics',
                        'Materials with new properties',
                        'Materials with substantial improvements to existing properties'
                        'Material property characterization and lifecycle assessment'
                    )
                )
            case 'Advanced Gas Turbine Engine Technologies':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Aerospace, maritime, and industrial development and production technologies',
                        'Full-authority digital engine control, hot-section manufacturing, and associated technologies'
                    )
                )
            case 'Advanced Manufacturing':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Additive manufacturing',
                        'Clean, sustainable manufacturing',
                        'Smart manufacturing',
                        'Nanomanufacturing'
                    )
                )
            case 'Advanced Networked Sensing and Signature Management':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Payloads, sensors, and instruments',
                        'Sensor processing and data fusion',
                        'Adaptive optics',
                        'Remote sensing of the Earth',
                        'Signature management',
                        'Nuclear materials detection and characterization',
                        'Chemical weapons detection and characterization',
                        'Biological weapons detection and characterization',
                        'Emerging pathogens detection and characterization',
                        'Transportation-sector sensing',
                        'Security-sector sensing',
                        'Health-sector sensing',
                        'Energy-sector sensing',
                        'Building-sector sensing',
                        'Environmental-sector sensing'
                    )
                )
            case 'Advanced Nuclear Energy Technologies':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Nuclear energy systems',
                        'Fusion energy',
                        'Space nuclear power and propulsion systems'
                    )
                )
            case 'Artificial Intelligence':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Machine learning',
                        'Deep learning',
                        'Reinforcement learning',
                        'Sensory perception and recognition',
                        'Next-generation AI',
                        'Planning, reasoning, and decision making',
                        'Safe and/or secure AI'
                    )
                )
            case 'Autonomous Systems and Robotics':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Surfaces',
                        'Air',
                        'Maritime',
                        'Space'
                    )
                )
            case 'Biotechnologies':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Nucleic acid and protein synthesis',
                        'Genome and protein engineering including design tools',
                        'Multi-omics and other biometrology, bioinformatics, predictive modeling, and analytical tools for functional phenotypes',
                        'Engineering of multicellular systems',
                        'Engineering of viral and viral delivery systems',
                        'Biomanufacturing and bioprocessing technologies'
                    )
                )
            case 'Communication and Networking Technologies':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Radio-frequency (RF) and mixed-signal circuits, antennas, filters, and components',
                        'Spectrum management technologies',
                        'Next-generation wireless networks, including 5G and 6G',
                        'Optical links and fiber technologies',
                        'Terrestrial/undersea cables',
                        'Satellite-based communications',
                        'Hardware, firmware, and software',
                        'Communications and network security',
                        'Mesh networks/infrastructure independent communication technologies'
                    )
                )
            case 'Directed Energy':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Lasers',
                        'High-power microwaves',
                        'Particle beams',
                        'Optical links and fiber technologies',
                        'Terrestrial/undersea cables',
                        'Satellite-based communications',
                        'Hardware, firmware, and software',
                        'Communications and network security',
                        'Mesh networks/infrastructure independent communication technologies'
                    )
                )
            case 'Financial Technologies':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Distributed ledger technologies',
                        'Digital assets',
                        'Digital payment technologies',
                        'Digital identity infrastructure'
                    )
                )
            case 'Human-Machine Interfaces':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Augmented reality',
                        'Virtual reality',
                        'Brain-computer interfaces',
                        'Human-machine teaming'
                    )
                )
            case 'Hypersonics':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Propulsion',
                        'Aerodynamics and control',
                        'Materials',
                        'Detection, tracking, and characterization',
                        'Defense'
                    )
                )
            case 'Quantum Information Technologies':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Quantum computing',
                        'Materials, isotopes, and fabrication techniques for quantum devices',
                        'Post-quantum cryptography',
                        'Quantum sensing',
                        'Quantum networking'
                    )
                )
            case 'Renewable Energy Generation and Storage':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Renewable generation',
                        'Renewable and sustainable fuels',
                        'Energy storage',
                        'Electric and hybrid engines',
                        'Batteries',
                        'Grid integration technologies',
                        'Energy-efficiency technologies'
                    )
                )
            case 'Semiconductors and Microelectronics':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'Design and electronic design automation tools',
                        'Manufacturing process technologies and manufacturing equipment',
                        'Beyond complementary metal-oxide-semiconductor (CMOS) technology',
                        'Heterogeneous integration and advanced packaging',
                        'Specialized/tailored hardware components for artificial intelligence, natural and hostile '
                        'radiation environments, RF and optical components, high-power devices, and other critical '
                        'applications',
                        'Novel materials for advanced microelectronics',
                        'Wide-bandgap and ultra-wide-bandgap technologies for power management, distribution, '
                        'and transmission '
                    )
                )
            case 'Space Technologies and Systems':
                subfield = st.selectbox(
                    label='Select a subfield:',
                    options=(
                        '-',
                        'On-orbit servicing, assembly, and manufacturing',
                        'Commoditized satellite buses',
                        'Low-cost launch vehicles',
                        'Sensors for local and wide-field imaging',
                        'Space propulsion',
                        'Resilient positioning, navigation, and timing (PNT)',
                        'Cryogenic fluid management',
                        'Entry, descent, and landing'
                    )
                )

        # Sidebar select box to choose date
        select_date = st.date_input(
            'Select a date:',
            date(2022, 5, 30)
        )

        # Submit button
        submit = st.form_submit_button()

    return subfield, select_date, submit


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
