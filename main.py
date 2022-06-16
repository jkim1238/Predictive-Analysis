import pandas as pd

from utils import *
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, DataReturnMode


def main():
    # Set page config
    st.set_page_config(
        page_title="Predictive Analysis",
        page_icon="❓",
        initial_sidebar_state='expanded'
    )

    # Initialization of session state variables
    if 'technology' not in st.session_state:
        st.session_state['technology'] = '-'
    if 'df' not in st.session_state:
        st.session_state['df'] = None
    if 'selected_df' not in st.session_state:
        st.session_state['selected_df'] = None
    if 'df_tech' not in st.session_state:
        st.session_state['df_tech'] = None
    if 'articles_count' not in st.session_state:
        st.session_state['articles_count'] = None

    # Set sidebar
    st.session_state['technology'], select_date = set_sidebar()

    if st.session_state['technology'] == '-':
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
           Select a technology, subfield, and date from the sidebar.
        """)
    else:
        # Display technology title
        st.title(st.session_state['technology'])

        # Convert datetime object to date string
        date_string = select_date.strftime('%Y%m%d')

        # Make technology lowercase
        technology_string = st.session_state["technology"].lower()

        # Replace spaces with underscore
        technology_string = technology_string.replace(' ', '_')

        if st.session_state['df_tech'] != st.session_state['technology']:
            # Clear page
            st.empty()
            st.empty()
            st.empty()
            st.empty()
            st.empty()

            # Get 'ARLIS' mongoDB database
            db = get_database()

            # Get articles and count from mongoDB collection
            articles, st.session_state["articles_count"] = get_collection(
                database=db,
                date=select_date,
                technology=st.session_state['technology']
            )

            # If there wasn't any previous articles in the database, use newscatcherapi and store in mongoDB Atlas
            # database
            if f'{date_string}_{technology_string}' not in db.list_collection_names():
                articles, st.session_state["articles_count"] = consume_api(
                    database=db,
                    date=select_date,
                    technology=st.session_state['technology']
                )

            # If there wasn't a previous prediction, calculate new prediction
            if f'{date_string}_{technology_string}_prediction' not in db.list_collection_names():
                with st.spinner('Please wait...'):
                    # Get company names using Name Entity Recognition and perform Sentiment Analysis on article text
                    companies = natural_language_processing(articles=articles)

                # Convert dictionary to list
                companies_list = dictionary_to_list(companies)

                # TODO Store companies in the database
                store_documents(
                    database=db,
                    document=companies_list,
                    date=select_date,
                    technology=st.session_state["technology"]
                )

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
                # Check if there was a previous prediction
                companies, companies_count = get_collection(
                    database=db,
                    date=select_date,
                    technology=f'{st.session_state["technology"]}_prediction'
                )

                # Convert cursor to dataframe
                df = pd.DataFrame(list(companies))

            # Sort dataframe by count
            if not df.empty:
                df.sort_values(
                    by='Count',
                    ascending=False,
                    inplace=True
                )

            # Set session state
            st.session_state['df_tech'] = st.session_state['technology']
            st.session_state['df'] = df

        # Display statistics
        st.write(
            f'There are {st.session_state["articles_count"]} articles on {st.session_state["technology"]} on {select_date.strftime("%Y/%m/%d")}.\n'
            f'Found {len(st.session_state["df"])} companies total.')

        # Grid options
        gb = GridOptionsBuilder.from_dataframe(st.session_state['df'])
        gb.configure_selection(
            selection_mode='multiple',
            use_checkbox=True
        )
        gb.configure_pagination()
        gb.configure_side_bar()
        gb.configure_default_column(
            groupable=True,
            value=True,
            enableRowGroup=True,
            aggFunc='sum',
            editable=True
        )
        gridOptions = gb.build()

        # Display dataframe
        selected_data = AgGrid(
            dataframe=st.session_state['df'],
            gridOptions=gridOptions,
            enable_enterprise_modules=True,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode=GridUpdateMode.MODEL_CHANGED
        )

        # Convert selected rows as dataframe
        st.session_state['selected_df'] = pd.DataFrame(selected_data['selected_rows'])

        # Set 2 columns for the options.
        col1, col2 = st.columns(2)

        with col1:
            # Save all raw data button to save DataFrame as CSV file.
            st.download_button(
                label='Download All Data',
                data=st.session_state['df'].to_csv(),
                file_name=f'{date_string}_{technology_string}.csv',
                mime='text/csv'
            )
        with col2:
            # Save selected raw data button to save DataFrame as CSV file.
            st.download_button(
                label='Download Selected Data',
                data=st.session_state['selected_df'].to_csv(),
                file_name=f'{date_string}_{technology_string}.csv',
                mime='text/csv'
            )


if __name__ == '__main__':
    main()
