import data
import psycopg2
import pandas as pd
import streamlit as st
import plotly.express as px
import os
import warnings
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime
warnings.filterwarnings("ignore")


# ustawienie parametrów okna głownego
st.set_page_config(page_title="MET_SEL_REPORT",
                   page_icon=":chart_with_upwards_trend:", layout="wide")

# ustawienie nagłówka h1
st.title(":chart_with_upwards_trend: KC Działu sprzedaży")
st.markdown(
    '<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)


###################################################################################################
# download data
###################################################################################################

df = data.download_data_to_df()
print(df)
# dodanie kolumny z rokiem i miesiacem
df['rok'] = pd.DatetimeIndex(df['data_wystawienia_wz']).year
df['miesiac'] = pd.DatetimeIndex(df['data_wystawienia_wz']).month
df['month_year'] = pd.to_datetime(df['data_wystawienia_wz']).dt.to_period('M')
df.head()

# pobranie danych do sledzenia wykonania rocznego budzetu
wykonanie_sprzedaz_rok = data.download_wykoanie_plan_roczny_to_df(2023)
print(wykonanie_sprzedaz_rok)

wykonanie_sprzedaz_rok['do_wykonania'] = wykonanie_sprzedaz_rok['wartosc_plan'] - \
    wykonanie_sprzedaz_rok['wartosc_sprzedazy']


##################################################################################################
###################################################################################################
st.sidebar.header("Choose your filter: ")
# Create for month_year
month_year = st.sidebar.multiselect("Wybierz okres", df["month_year"].unique())

# Create for client
client = st.sidebar.multiselect("Klient", df["klient_sp"].unique())

# miesiac do analizy miesiaca
# month = st.sidebar.selectbox("Wybierz okres", df["month_year"].unique())
month = st.sidebar.selectbox(
    "Wybierz okres", df["month_year"].dt.strftime('%Y-%m').unique())


# Filter the data based on month_year and client:
if not month_year and not client:
    filtered_df = df
elif not month_year:
    filtered_df = df[df["klient_sp"].isin(client)]
elif not client:
    filtered_df = df[df["month_year"].isin(month_year)]
elif month_year and client:
    filtered_df = df[df["month_year"].isin(
        month_year) & df["klient_sp"].isin(client)]

# create chart
# sprzedaż od początku bieżącego roku
sale_current_year_df = df.groupby(by=["klient_sp"], as_index=False)[
    "wartosc_poz_pln"].sum()
sale_current_year_df = sale_current_year_df.sort_values(
    by=['wartosc_poz_pln'], ascending=False)

# test barchart
test_df = df.groupby(by=['klient_sp', 'zaplacono',], as_index=False)[
    ['wartosc_poz_pln']].sum()


sale_current_year_df2 = data.download_wykoanie_plan_roczny_to_df(2023)
sale_current_year_df2 = sale_current_year_df2.sort_values(
    by=['wartosc_sprzedazy'], ascending=False)

##############################################################################
# REALIZACJA PLAN ROCZNY
##############################################################################

exec_year_budg = data.get_realizacja_plan_roczny()
# Combine 'Year' and 'Month' columns into a 'Date' column
# st.write(exec_year_budg)
exec_year_budg['Date'] = pd.to_datetime(exec_year_budg['rok'].astype(str) +
                                        exec_year_budg['msc'].astype(str), format='%Y%m')


col1, col2 = st.columns([3, 1])
# WYKRES 1 sprzedaż bierzący rok
with col1:
    # trace1 = go.Scatter(
    #     mode='lines',
    #     x=sale_current_year_df2['klient_sp'],
    #     y=sale_current_year_df2['wartosc_plan'],
    #     name="Percentage Cases",
    #     marker_color='crimson'
    # )
    sprzedaz_rok_plan = sale_current_year_df2['wartosc_plan'].sum()
    foramted_sprzedaz_rok_plan = "{:,.0f}".format(
        sprzedaz_rok_plan)
    sprzedaz_rok_zrealizowana = sale_current_year_df2['wartosc_sprzedazy'].sum(
    )
    foramted_sprzedaz_rok_zrealizowana = "{:,.0f}".format(
        sprzedaz_rok_zrealizowana)
    st.subheader(
        f"Sprzedaż bieżący rok | wartość: {foramted_sprzedaz_rok_zrealizowana.replace(',', ' ')} PLN | Plan:{foramted_sprzedaz_rok_plan.replace(',', ' ')} PLN ")
    # st.subheader("Sprzedaż bieżący rok")

    ###############################################
    # wykres roczny realizacja narastajaca
    ###############################################
    year_exec = px.line(x=exec_year_budg['Date'], y=exec_year_budg['plan'], color=px.Constant("plan"),
                        labels=dict(y="wartosc tys. PLN", x="data", color="Time Period"), template="simple_white")
    year_exec.add_scatter(
        x=exec_year_budg['Date'], y=exec_year_budg['sprzedaz'], mode='lines')

    st.plotly_chart(year_exec, use_container_width=True, height=200)
    ###############################################
    # wykres roczny plan wyk
    ###############################################
    fig = px.line(x=sale_current_year_df2['klient_sp'], y=sale_current_year_df2['wartosc_plan'], color=px.Constant("Plan"),
                  labels=dict(x="Klient", y="Sprzedaż", color="Time Period"), template="simple_white")
    fig.add_bar(x=sale_current_year_df2['klient_sp'], y=sale_current_year_df2['wartosc_sprzedazy'], name="Sprzedaż", text=[
                'PLN {:,.0f}'.format(round(x, -3) / 1000).replace(",", " ") for x in sale_current_year_df2["wartosc_sprzedazy"]])

    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.write(sale_current_year_df2)
    # for showing values with a thousands space on bar
# formatted_y = [f"{test_df["wartosc_poz_pln"]:,}".replace(",", " ").split(".")[0] for x in y]

# WYKRES sprzedaż bullet rok
# st.subheader("Realizacja celów rocznych")
# fig_bullet_chart_annual = go.Figure(go.Indicator(
#     mode="number+gauge+delta",
#     gauge={'shape': "bullet"},
#     value=wykonanie_sprzedaz_rok['wartosc_sprzedazy'].sum(),
#     delta={'reference': wykonanie_sprzedaz_rok['wartosc_plan'].sum()},
#     domain={'x': [0, 1], 'y': [0, 1]},
#     title={'text': "Profit"}))
# fig.update_layout(height=250)
# st.plotly_chart(fig_bullet_chart_annual, use_container_width=True)
# Create a bullet chart for each klient_sp

#####################################################################################
    # ANALIZA BIERZACEGO LUB WYBRANEGO MIESIACA
#####################################################################################
with st.container():
    st.write(df)
    # st.subheader(f"Sprzedaż wybrany miesiąc {month}")
    # st.write(type(month))
    msc_data = df[df.month_year == month]
    # Konwersja wybranego okresu na datetime
    # st.write(month)
    rok_to_mnt_analyze = month[:4]
    month_to_mnt_analyze = [int(month[-2:])]
    df_selected_month = data.download_wykoanie_plan_roczny_to_df(
        rok_to_mnt_analyze, month_to_mnt_analyze)
    df_selected_month = df_selected_month.sort_values(
        by=['wartosc_sprzedazy'], ascending=False)

    sprzedaz_mnt_plan = df_selected_month['wartosc_plan'].sum()
    foramted_sprzedaz_mnt_plan = "{:,.0f}".format(
        sprzedaz_mnt_plan)
    sprzedaz_mnt_zrealizowana = df_selected_month['wartosc_sprzedazy'].sum()
    foramted_sprzedaz_mnt_zrealizowana = "{:,.0f}".format(
        sprzedaz_mnt_zrealizowana)

col11, col22 = st.columns([3, 1])
with col11:
    st.subheader(
        f"Sprzedaż wybrany miesiac {month} | wartość: {foramted_sprzedaz_mnt_zrealizowana.replace(',', ' ')} PLN | Plan:{foramted_sprzedaz_mnt_plan.replace(',', ' ')} PLN ")
    fig_mnth = px.line(x=df_selected_month['klient_sp'], y=df_selected_month['wartosc_plan'], color=px.Constant("Plan"),
                       labels=dict(x="Klient", y="Sprzedaż", color="Time Period"), template="simple_white")
    fig_mnth.add_bar(x=df_selected_month['klient_sp'], y=df_selected_month['wartosc_sprzedazy'], name="Sprzedaż", text=[
        'PLN {:,.0f}'.format(round(x, -3) / 1000).replace(",", " ") for x in df_selected_month["wartosc_sprzedazy"]])
    # fig.add_line(
    #     x=sale_current_year_df2['klient_sp'], y=sale_current_year_df2['wartosc_plan'])
    st.plotly_chart(fig_mnth, use_container_width=True, height=200)

with col22:
    st.write(df_selected_month)

# if (month_year isnull):
#     current_month = pd.DataFrame({'Current_Date': [datetime.now().date()]})
# else:
#     current_month = month_year
with st.container():
    month = pd.DataFrame({'Current_Date': [datetime.now().date()]})
    st.write(month)

    kod_msc = pd.to_datetime(month['Current_Date']).dt.to_period('M')

    # st.write(kod_msc)
    # st.write(df)

    st.write(kod_msc)

col111, col222 = st.columns([3, 1])
with col111:
    data = [
        {"label": "revenue",
         "sublabel": "us$, in thousands",
         "range": [150, 225, 300],
         "performance": [220, 270],
         "point": [250]},

        {"label": "Profit",
         "sublabel": "%",
         "range": [20, 25, 30],
         "performance": [21, 23],
         "point": [26]},

        {"label": "Order Size",
         "sublabel": "US$, average",
         "range": [350, 500, 600],
         "performance": [100, 320],
         "point": [550]},

        {"label": "New Customers",
         "sublabel": "count",
         "range": [1400, 2000, 2500],
         "performance": [1000, 1650],
         "point": [2100]},

        {"label": "Satisfaction",
         "sublabel": "out of 5",
         "range": [3.5, 4.25, 5],
         "performance": [3.2, 4.7],
         "point": [4.4]}
    ]

    fig66 = ff.create_bullet(
        data, titles='label',
        subtitles='sublabel',
        markers='point',
        measures='performance',
        ranges='range',
        orientation='h',
        title='my simple bullet chart'
    )

    st.plotly_chart(fig66)
# wykres test bullet
    fig_test = go.Figure()

    fig_test.add_trace(go.Indicator(
        mode="number+gauge+delta", value=180,
        delta={'reference': 200},
        domain={'x': [0.25, 1], 'y': [0.08, 0.25]},
        title={'text': "Revenue"},
        gauge={
            'shape': "bullet",
            'axis': {'range': [None, 300]},
            'threshold': {
                'line': {'color': "black", 'width': 2},
                'thickness': 0.75,
                'value': 170},
            'steps': [
                {'range': [0, 150], 'color': "gray"},
                {'range': [150, 250], 'color': "lightgray"}],
            'bar': {'color': "black"}}))

    fig_test.add_trace(go.Indicator(
        mode="number+gauge+delta", value=400,
        delta={'reference': 200},
        domain={'x': [0.25, 1], 'y': [0.55, 0.65]},
        title={'text': "Revenue_TEST"},
        gauge={
            'shape': "bullet",
            'axis': {'range': [None, 300]},
            'threshold': {
                'line': {'color': "black", 'width': 2},
                'thickness': 0.75,
                'value': 170},
            'steps': [
                {'range': [0, 150], 'color': "green"},
                {'range': [150, 250], 'color': "lightgray"}],
            'bar': {'color': "black"}}))

    fig_test.add_trace(go.Indicator(
        mode="number+gauge+delta", value=400,
        delta={'reference': 200},
        domain={'x': [0.25, 1], 'y': [0.75, 0.85]},
        title={'text': "Revenue_TEST"},
        gauge={
            'shape': "bullet",
            'axis': {'range': [None, 300]},
            'threshold': {
                'line': {'color': "black", 'width': 2},
                'thickness': 0.75,
                'value': 170},
            'steps': [
                {'range': [0, 150], 'color': "gray"},
                {'range': [150, 250], 'color': "lightgray"}],
            'bar': {'color': "black"}}))

    fig_test.add_trace(go.Indicator(
        mode="number+gauge+delta", value=220,
        delta={'reference': 200},
        domain={'x': [0.25, 1], 'y': [0.9, 1.0]},
        title={'text': "Satisfaction"},
        gauge={
            'shape': "bullet",
            'axis': {'range': [None, 300]},
            'threshold': {
                'line': {'color': "black", 'width': 2},
                'thickness': 0.75,
                'value': 210},
            'steps': [
                {'range': [0, 150], 'color': "gray"},
                {'range': [150, 250], 'color': "lightgray"}],
            'bar': {'color': "black"}}))
    fig_test.update_layout(height=400, margin={'t': 0, 'b': 0, 'l': 0})

    st.plotly_chart(fig_test)
# WYKRES 2
    barchart = px.bar(
        test_df,
        x="klient_sp",
        y="wartosc_poz_pln",
        color="zaplacono",               # differentiate color of marks
        opacity=0.9,                  # set opacity of markers (from 0 to 1)
        orientation="v",              # 'v','h': orientation of the marks
        # in 'overlay' mode, bars are top of one another.
        barmode='relative',
        # color_discrete_map={"TAK": "gray", "NIE": "red"}
        color_discrete_sequence=px.colors.qualitative.Pastel,

        labels={"convicts": "Convicts in Maharashtra",
                "zaplacono": "Zaplacono"},           # map the labels of the figure
        title='Sprzedaż roczna',  # figure title
        width=1400,                   # figure width in pixels
        height=720,                   # figure height in pixels
        template='gridon',
        # values appear in figure as text labels
        text=['PLN {:,.0f}'.format(round(x, -3) / 1000).replace(",", " ")
              for x in test_df["wartosc_poz_pln"]],
        hover_name=['PLN {:,.0f} k'.format(round(x, -3) / 1000).replace(",", " ")
                    for x in test_df["wartosc_poz_pln"]],   # values appear in bold in the hover tooltip
        # values appear as extra data in the hover tooltip
        hover_data=['wartosc_poz_pln'],
        # invisible values that are extra data to be used in Dash callbacks or widgets
        custom_data=['wartosc_poz_pln'],
    )
    # tickformat = ',.0f'.replace(",", " ")  # Set the thousands separator format
    # Dostosowanie osi Y
    barchart.update_layout(
        yaxis=dict(
            # tickformat=tickformat,
            title='Wartość w tysiącach'
        ),
        xaxis=dict(
            title='Klient'
        ),
        # title='Wykres słupkowy z separatorem tysięcznym'
    )
    st.plotly_chart(barchart, use_container_width=True, height=200)

# WYKRES 3
    # fake margin of error, standard deviation, or 95% confidence interval
    wykonanie_sprzedaz_rok['err_plus'] = wykonanie_sprzedaz_rok['wartosc_plan'] - \
        wykonanie_sprzedaz_rok['wartosc_sprzedazy']
    # df['err_minus'] = df['convicts']/40

    wykres_wyk_rok = px.bar(
        wykonanie_sprzedaz_rok,
        x="klient_sp",
        y="wartosc_sprzedazy",
        # color="zaplacono",               # differentiate color of marks
        # set opacity of markers (from 0 to 1)
        opacity=0.9,
        orientation="v",              # 'v','h': orientation of the marks
        # in 'overlay' mode, bars are top of one another.
        barmode='relative',
        # color_discrete_map={"TAK": "gray", "NIE": "red"}
        color_discrete_sequence=px.colors.qualitative.Pastel,

        labels={"convicts": "Convicts in Maharashtra",
                    "klient_sp": "klient_sp"},           # map the labels of the figure
        title='Sprzedaż roczna vs plan',  # figure title
        width=1400,                   # figure width in pixels
        height=720,                   # figure height in pixels
        template='gridon',
        # values appear in figure as text labels
        # text=['PLN {:,.0f}'.format(round(x, -3) / 1000).replace(",", " ")
        #       for x in test_df["wartosc_sprzedazy"]],
        # hover_name=['PLN {:,.0f} k'.format(round(x, -3) / 1000).replace(",", " ")
        #             for x in test_df["wartosc_sprzedazy"]],   # values appear in bold in the hover tooltip
        # values appear as extra data in the hover tooltip
        # hover_data=['wartosc_sprzedazy'],
        # invisible values that are extra data to be used in Dash callbacks or widgets
        # custom_data=['wartosc_sprzedazy'],
        # y-axis error bars are symmetrical or for positive direction
        error_y="err_plus",
        # y-axis error bars in the negative direction
        error_y_minus="wartosc_sprzedazy",
    )
    tickformat = ',.0f'.replace(",", " ")  # Set the thousands separator format
    # Dostosowanie osi Y
    wykres_wyk_rok.update_layout(
        yaxis=dict(
            # tickformat=tickformat,
            title='Wartość w tysiącach'
        ),
        xaxis=dict(
            title='Klient'
        ),
        # title='Wykres słupkowy z separatorem tysięcznym'
    )
    st.plotly_chart(wykres_wyk_rok, use_container_width=True, height=200)


##########################################################################################
# podgląd danych z mozliwoascią pobrania pliku CSV
##########################################################################################
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Sprzedaż bierzący rok"):
        st.write(sale_current_year_df.style.background_gradient(cmap="Blues"))
        csv = sale_current_year_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="sale_current_year_df.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')
with cl2:
    # podgląd danych z mozliwoascią pobrania pliku CSV
    with st.expander("test"):
        st.write(test_df.style.background_gradient(cmap="Blues"))
        csv = test_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="test_df.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')
