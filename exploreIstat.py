import streamlit as st
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

from utils import get_dataset

def print_corr(df:pd.DataFrame):
    st.write("Correlation Pearson")
    #fig = px.imshow(df.corr())
    #st.plotly_chart(fig,use_container_width=True)
    fig = go.Figure(data=go.Heatmap(
                    z=df.corr(),
                    x=df.columns,
                    y=df.columns,
                    hovertemplate = "%{x} <br>%{y} <br>%{z}"))
    st.plotly_chart(fig,use_container_width=True)

    st.write("Correlation Kendall")
    #fig = px.imshow(df.corr('kendall'))
    fig = go.Figure(data=go.Heatmap(
                    z=df.corr('kendall'),
                    x=df.columns,
                    y=df.columns,
                    hovertemplate = "%{x} <br>%{y} <br>%{z}"))
    st.plotly_chart(fig,use_container_width=True)

    st.write("Correlation Spearman")
    #fig = px.imshow(df.corr('spearman'))
    fig = go.Figure(data=go.Heatmap(
                    z=df.corr('spearman'),
                    x=df.columns,
                    y=df.columns,
                    hovertemplate = "%{x} <br>%{y} <br>%{z}"))
    st.plotly_chart(fig,use_container_width=True)

def join_and_plot(df1:pd.DataFrame, df2:pd.DataFrame):
    print_corr(df1.join(df2))

df_province, df_regioni, smokers_series, imprese_series, air_series  = get_dataset(date.today())

cols = [c for c in df_regioni.columns if 'Popolazione' in c or 'NUTS3' in c]
pop_series_reg = df_regioni[cols].set_index('NUTS3')

cols = [c for c in df_province.columns if 'Popolazione' in c or 'NUTS3' in c]
pop_series = df_province[cols].set_index('NUTS3')


cols = [c for c in df_regioni.columns if not 'Popolazione' in c]
df_regioni = df_regioni[cols]

cols = [c for c in df_province.columns if not 'Popolazione' in c]
df_province = df_province[cols]

df_regioni_today = df_regioni.set_index("NUTS3")
df_regioni_today = df_regioni_today[df_regioni_today["data"] == df_regioni_today["data"].max()]
df_province_today = df_province.set_index("NUTS3")      
df_province_today = df_province_today[df_province_today["data"] == df_province_today["data"].max()]

##########################################################################################################################################
######################################################   DROP USELESS COLUMNS   ##########################################################
##########################################################################################################################################

df_regioni_today = df_regioni_today.drop(columns=['data', 'stato', 'codice_regione', 'denominazione_regione', 'lat', 'long', 'note_it', 'note_en', 'codice_storico', 'giorno'], axis=1)
df_province_today = df_province_today.drop(columns=['data', 'stato', 'codice_regione', 'denominazione_regione', 'codice_provincia', 'denominazione_provincia', 'sigla_provincia', 'lat', 'lon', 'note_it', 'note_en', 'giorno'], axis=1)

##########################################################################################################################################
#########################################################   VISUALIZATION   ##############################################################
##########################################################################################################################################
st.write("REGIONI")
st.write('Popolazione')
join_and_plot(df_regioni_today, pop_series_reg)

st.write('Fumatori')
join_and_plot(df_regioni_today, smokers_series)

st.write('Inquinamento')
air_reg_series = air_series.drop(columns=["CODICE PROVINCIA", "COMUNI", "denominazione_regione"]).pivot_table(index='NUTS3_regione')
join_and_plot(df_regioni_today, air_reg_series)

st.write('Imprese')
join_and_plot(df_regioni_today, imprese_series)

##########################################################################################################################################

st.write("PROVINCE")
st.write('Popolazione')
join_and_plot(df_province_today, pop_series)

st.write('Inquinamento')
join_and_plot(df_province_today, air_series.drop(columns=['denominazione_regione', "COMUNI", "CODICE PROVINCIA", "NUTS3_regione"]))
