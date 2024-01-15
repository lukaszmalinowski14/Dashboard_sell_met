import streamlit as st
import pandas as pd

# Tworzenie przykładowego DataFrame
data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
df = pd.DataFrame(data)

# Dodanie kolumny
col1, col2 = st.columns(2)

# Dodanie danych bez podziału na kolumny
with col1:
    st.header('Dane bez podziału na kolumny')
    st.write(df)

# Dodanie poziomej linii oddzielającej
st.markdown("---")
with st.container():
    st.write(
        '### This is a containergdfffffffffffffffffffffffffffffffffffffffffffffffffffff.')

# Dodanie danych z podziałem na kolumny
with col2:
    st.header('Dane z podziałem na kolumny')
    st.dataframe(df)

# Dodanie ponownego podziału kolumny
col3, col4 = st.columns(2)

# Dodanie danych do pierwszej nowej kolumny
with col3:
    st.header('Nowe dane bez podziału na kolumny')
    st.write(df)

# Dodanie poziomej linii oddzielającej
st.markdown("---")

# Dodanie danych do drugiej nowej kolumny
with col4:
    st.header('Nowe dane z podziałem na kolumny')
    st.dataframe(df)
