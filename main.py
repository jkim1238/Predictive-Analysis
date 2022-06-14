import streamlit as st
import pandas as pd
from utils import *
from datetime import date
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder


def main():
    # Set page config
    st.set_page_config(
        page_title="Predictive Analysis",
        page_icon="❓",
        initial_sidebar_state='expanded'
    )

    # Declare a form to handle a submit button
    with st.sidebar.form(key='my_form'):
        # Display form title
        st.write('Predictive Analysis')

        # Sidebar select box to choose critical technology subfield
        technology = st.selectbox(
            label='Select a technology:',
            options=('-', 'Cloud Computing')
        )

        # Sidebar select box to choose date
        select_date = st.date_input(
            'Select a date:',
            date(2022, 5, 30)
        )

        # Submit button
        submit = st.form_submit_button()

    if not submit or technology == '-':
        # Print title
        st.title(
            body='❓ AL - CFIUS Over the Horizon Forecasting for Critical and Emerging Technologies',
            anchor='title'
        )

        # Print team member names
        st.write("""
        08/Sponsor: OUSD (I&S) CL&S\n
        USG Champion: Kristoffer Buquet, Chief TechProject Div\n
        Faculty Mentor: Christopher Nissen, UMD Applied Research Laboratory for Intelligence and Security\n
        Interns: Lauren Shanley-DeBuse, Danielle Mixon, Jiin Kim
        """)

        # Summary header
        st.header(body='Summary')

        # Print project summary
        st.write("""
        The Foreign Ownership, Control, and Influence (FOCI) threat to our current and future Critical
        and Emerging Technologies continues to grow and become more invasive. The is further
        compounded by the direct foreign investment, both private sector and Foreign Government
        Control, in U.S. companies as highlighted by the Committee for the Foreign Investment in the
        U.S. (CFIUS) process.\n
        This project would focus on an identified technology area/sector, and the U.S. companies
        working on or directly supporting the identified technology. The scoped example would be to
        define companies working on our Critical and Emerging Technologies (C&ET) down to the CAGE
        code as they relate to the identified technology, and as determined based on a defined
        proximity to a DoD facility/installation.
        """)

        # Getting started header
        st.header('Getting Started')

        # Print instructions
        st.write("""
           Select a technology and date from the sidebar.
        """)
    else:
        # Get 'ARLIS' mongoDB database
        db = get_database()

        # Check if there was a previous prediction
        companies, companies_count = get_collection(
            database=db,
            date=select_date,
            technology=f'{technology}_prediction'
        )

        # Get articles and count from mongoDB collection
        articles, articles_count = get_collection(
            database=db,
            date=select_date,
            technology=technology
        )

        # If there wasn't a previous prediction, calculate new prediction
        if not companies:
            # Get company names using Name Entity Recognition and perform Sentiment Analysis on article text
            companies = natural_language_processing(articles=articles)

            # Convert dictionary to list
            companies_list = dictionary_to_list(companies)

            # TODO Store companies in the database
            # store_documents(database=db, document=companies_list, date=select_date, technology=technology)

            # Convert dictionary to pandas dataframe
            df = pd.concat({k: pd.DataFrame.from_dict(v, 'index') for k, v in companies.items()}, axis=0).reset_index()

            # Drop empty columns
            df.drop(
                columns=['level_1'],
                inplace=True
            )

            # Rename columns
            df.columns = ['Name', 'Count']
        else:
            # Convert cursor to dataframe
            df = pd.DataFrame(list(companies))

        # Sort dataframe by count
        df.sort_values(
            by='Count',
            ascending=False,
            inplace=True
        )

        # Display technology title
        st.title(technology)

        # Display statistics
        st.write(f'There are {articles_count} articles on {technology} on {select_date.strftime("%Y/%m/%d")}.\n'
                 f'Found {companies_count} companies total.')

        # Grid options
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_side_bar()
        gb.configure_default_column(
            groupable=True,
            value=True,
            enableRowGroup=True,
            aggFunc="sum",
            editable=True
        )
        gridOptions = gb.build()

        # Display dataframe
        AgGrid(
            dataframe=df,
            gridOptions=gridOptions,
            enable_enterprise_modules=True
        )


if __name__ == '__main__':
    main()
