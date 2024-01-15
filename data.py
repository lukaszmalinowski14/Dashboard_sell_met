import psycopg2
import pandas as pd
from psycopg2 import sql
import streamlit as st
from datetime import datetime

# PostgreSQL database connection parameters
db_params = {
    'host': "10.1.5.30",
    'user': 'testdbuser',
    'password': 'Xai7aer7pu',
    'database': 'pimstalnew'
}

# Function to download data from PostgreSQL to Pandas DataFrame


@st.cache_data
def download_data_to_df():
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(**db_params)

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    try:
        # Execute the SQL query to get data from the function
        query = "SELECT * FROM meteurosystem.sprzedaz_dane();"
        cursor.execute(query)

        # Fetch all the rows from the query result
        rows = cursor.fetchall()

        # Get the column names from the cursor description
        columns = [desc[0] for desc in cursor.description]

        # Create a Pandas DataFrame from the query result
        df = pd.DataFrame(rows, columns=columns)

        return df

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


# Download data to Pandas DataFrame
# result_df = download_data_to_df()

####################################################################################################
# get budget#########################################################################################
####################################################################################################
@st.cache_data
def download_budget_to_df():
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(**db_params)

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    try:
        # Execute the SQL query to get data from the function
        query = "SELECT * FROM meteurosystem.sprzedaz_dane();"
        cursor.execute(query)

        # Fetch all the rows from the query result
        rows = cursor.fetchall()

        # Get the column names from the cursor description
        columns = [desc[0] for desc in cursor.description]

        # Create a Pandas DataFrame from the query result
        df = pd.DataFrame(rows, columns=columns)

        return df

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

####################################################################################################
# get budget#########################################################################################
####################################################################################################


@st.cache_data
def download_wykoanie_plan_roczny_to_df(rok=2023, month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]):
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(**db_params)

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    try:
        # Execute the SQL query to get data from the function
        # query = " select * from meteurosystem.wykonanie_sprzedaz_rok(%s);"
        # cursor.execute(query, rok)

        # Zapytanie SQL
        query = sql.SQL(
            "select * from meteurosystem.wykonanie_sprzedaz_rok(%s,%s)")

    # Wykonanie zapytania
        cursor.execute(query, (rok, month))

        # Fetch all the rows from the query result
        rows = cursor.fetchall()

        # Get the column names from the cursor description
        columns = [desc[0] for desc in cursor.description]

        # Create a Pandas DataFrame from the query result
        df = pd.DataFrame(rows, columns=columns)

        return df

    finally:
        # Close the cursor and connection
        cursor.close()


@st.cache_data
def download_nie_sklas_wz():
    pass
    # select * from meteurosystem.brak_kod_budzet()


@st.cache_data
def get_realizacja_plan_roczny(rok=2023):
    # select * from meteurosystem.wykonanie_sprzedaz_rok_narast(2023)
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(**db_params)

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    try:
        # Execute the SQL query to get data from the function
        # query = " select * from meteurosystem.wykonanie_sprzedaz_rok(%s);"
        # cursor.execute(query, rok)

        # Zapytanie SQL
        query = sql.SQL(
            "select * from meteurosystem.wykonanie_sprzedaz_rok_narast(%s)")

    # Wykonanie zapytania
        cursor.execute(query, (rok,))

        # Fetch all the rows from the query result
        rows = cursor.fetchall()

        # Get the column names from the cursor description
        columns = [desc[0] for desc in cursor.description]

        # Create a Pandas DataFrame from the query result
        df = pd.DataFrame(rows, columns=columns)

        print(df)
        return df

    finally:
        # Close the cursor and connection
        cursor.close()
