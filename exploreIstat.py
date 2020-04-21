import os
import streamlit as st
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

from utils import get_dataset, check_ds_istat

def print_corr(df:pd.DataFrame):
    #fig = px.imshow(df.corr())
    fig = go.Figure(data=go.Heatmap(
                    z=df,
                    x=df.columns,
                    y=df.columns,
                    hovertemplate = "%{x} <br>%{y} <br>%{z}"))
    
    return fig

def join_and_plot(df1:pd.DataFrame, df2:pd.DataFrame):
    if corr_filter == "Pearson":
        st.write("Correlation Pearson")
        fig = print_corr(df1.join(df2).corr())
    elif corr_filter == "Kendall":
        st.write("Correlation Kendall") 
        fig = print_corr(df1.join(df2).corr('kendall'))
    else:
        st.write("Correlation Spearman")
        fig = print_corr(df1.join(df2).corr('spearman'))
    
    st.plotly_chart(fig,use_container_width=True)

codici_regioni = ["ITG2", "ITG1", "ITF6", "ITF5", "ITF4", "ITF3", "ITF2", "ITF1", "ITE4", "ITE3", "ITE2", "ITE1", "ITD5", "ITC3", "ITD4", "ITD3", "ITD1", "ITD2", "ITC4", "ITC2", "ITC1"]

df_province, df_regioni, smokers_series, imprese_series, air_series  = get_dataset(date.today())

air_reg_series = air_series.drop(columns=["CODICE PROVINCIA", "COMUNI", "denominazione_regione"]).pivot_table(index='NUTS3_regione')

df_regioni_today = df_regioni[df_regioni["data"] == df_regioni["data"].max()]

df_province_today = df_province[df_province["data"] == df_province["data"].max()]

cols = [c for c in df_regioni_today.columns if 'Popolazione' in c or 'NUTS3' in c or 'data' in c]
pop_series_reg = df_regioni_today[cols].set_index('NUTS3')

cols = [c for c in df_province_today.columns if 'Popolazione' in c or 'NUTS3' in c or 'data' in c]
pop_series = df_province_today[cols].set_index('NUTS3')


cols = [c for c in df_regioni_today.columns if not 'Popolazione' in c]
df_regioni_today = df_regioni_today[cols].set_index("NUTS3")

cols = [c for c in df_province_today.columns if not 'Popolazione' in c]
df_province_today = df_province_today[cols].set_index("NUTS3")



##########################################################################################################################################
#########################################################   LOAD NEW DATA   ##############################################################
##########################################################################################################################################

check_ds_istat()

malati_path = os.path.join("ISTAT_DATA", "Malati.csv")
if os.path.exists(malati_path):
    malati_series_reg = pd.read_csv(malati_path).set_index("ITTER107")
else:
    malati_path = os.path.join("ISTAT_DATA", "DCCV_AVQ_PERSONE_17042020153238688.csv")
    malati = pd.read_csv(malati_path).drop(columns=["TIME", "Seleziona periodo", "Flag Codes", "Flags", "TIPO_DATO_AVQ", "Territorio"], axis=1)
    malati = malati[malati["MISURA_AVQ"]=="THV"]
    malati = malati.pivot_table(index=["ITTER107"], columns=[ "Tipo dato"], values='Value')
    malati_series_reg = malati.drop(index=["2", "3", "6", "7", "8", "9", "IT", "ITC", "ITD", "ITCD", "ITDA", "ITE", "ITF", "ITFG", "ITG"])
    malati_series_reg.to_csv(os.path.join("ISTAT_DATA", "Malati.csv"))
#st.write(malati_series_reg)

bmi_path = os.path.join("ISTAT_DATA", "BMI.csv")
if os.path.exists(bmi_path):
    bmi_series_reg = pd.read_csv(bmi_path).pivot_table(index="ITTER107")
else:
    bmi_path = os.path.join("ISTAT_DATA", "DCCV_AVQ_PERSONE1_17042020152434760.csv")
    bmi_reg = pd.read_csv(bmi_path).drop(columns=["Seleziona periodo", "SEXISTAT1", "Sesso", "Territorio", "TIPO_DATO_AVQ", "Flag Codes", "Flags"], axis=1)
    bmi_reg = bmi_reg[bmi_reg["MISURA_AVQ"]=="THV"]
    bmi_reg = bmi_reg[bmi_reg["TIME"]==bmi_reg.TIME.max()].drop(columns=["TIME"], axis=1)
    bmi_reg = bmi_reg.pivot_table(index=["ITTER107"], columns=["Tipo dato"], values='Value')
    bmi_series_reg = bmi_reg.drop(index=["2", "3", "6", "7", "8", "9", "IT", "ITC", "ITCD", "ITD", "ITDA", "ITE", "ITF", "ITFG", "ITG"])
    bmi_series_reg.to_csv(os.path.join("ISTAT_DATA", "BMI.csv"))

pov_fam_path = os.path.join("ISTAT_DATA", "Pov_Fam.csv")
if os.path.exists(pov_fam_path):
    pov_fam_series_reg = pd.read_csv(pov_fam_path).pivot_table(index="ITTER107")
else:
    pov_fam_path = os.path.join("ISTAT_DATA", "DCCV_POVERTA_17042020152758777.csv")
    pov_fam_reg = pd.read_csv(pov_fam_path).drop(columns=["Seleziona periodo", "Flag Codes", "Flags", "TIPO_DATO8", "Tipo dato", "Territorio"], axis=1)
    pov_fam_reg = pov_fam_reg[pov_fam_reg["TIME"]==pov_fam_reg.TIME.max()].drop(columns=["TIME"], axis=1)
    pov_fam_series_reg = pov_fam_reg.set_index("ITTER107").drop(index="IT").rename(columns={"Value":"Pov_Fam"})
    pov_fam_series_reg.to_csv(os.path.join("ISTAT_DATA", "Pov_Fam.csv"))

pov_ind_path = os.path.join("ISTAT_DATA", "Pov_Ind.csv")
if os.path.exists(pov_ind_path):
    pov_ind_series_reg = pd.read_csv(pov_ind_path).pivot_table(index="ITTER107")
else:
    pov_ind_path = os.path.join("ISTAT_DATA", "DCCV_POVERTA_17042020152721446.csv")
    pov_ind_reg = pd.read_csv(pov_ind_path).drop(columns=["Seleziona periodo", "Flag Codes", "Flags", "TIPO_DATO8", "Tipo dato", "Territorio"], axis=1)
    pov_ind_reg = pov_ind_reg[pov_ind_reg["TIME"]==pov_ind_reg.TIME.max()].drop(columns=["TIME"], axis=1)
    pov_ind_series_reg = pov_ind_reg.set_index(["ITTER107"]).drop(index=["IT", "ITC", "ITCD", "ITD", "ITDA", "ITE", "ITF", "ITFG", "ITG"]).rename(columns={"Value":"Pov_Ind"})
    pov_ind_series_reg.to_csv(os.path.join("ISTAT_DATA", "Pov_Ind.csv"))

causa_morte_path = os.path.join("ISTAT_DATA", "DCIS_CMORTE1_EV_17042020153004669.csv")
causa_morte = pd.read_csv(causa_morte_path).drop(columns=["TIME", "Seleziona periodo", "Flag Codes", "Flags", "TIPO_DATO15", "Tipo dato", "Sesso", "CAUSEMORTE_SL", "Territorio"], axis=1)

causa_morte_series_reg = causa_morte[causa_morte["ITTER107"].isin(codici_regioni+["ITD20", "ITD10"])].replace({"ITD20":"ITD2", "ITD10":"ITD1"})
causa_morte_series_reg_m = causa_morte_series_reg[causa_morte_series_reg["SEXISTAT1"]==1].pivot_table(index=["ITTER107"], columns=["Causa iniziale di morte - European Short List"], values='Value')
causa_morte_series_reg_f = causa_morte_series_reg[causa_morte_series_reg["SEXISTAT1"]==2].pivot_table(index=["ITTER107"], columns=["Causa iniziale di morte - European Short List"], values='Value')
causa_morte_series_reg_tot = causa_morte_series_reg[causa_morte_series_reg["SEXISTAT1"]==9].pivot_table(index=["ITTER107"], columns=["Causa iniziale di morte - European Short List"], values='Value')
#st.write(causa_morte_series_reg_tot)
causa_morte = causa_morte[~causa_morte["ITTER107"].isin(codici_regioni)].set_index("ITTER107").drop(index=["IT", "ITC", "ITD", "ITDA", "ITE", "ITF", "ITG"])#, "ITCD", "ITFG"
causa_morte_series_m = causa_morte[causa_morte["SEXISTAT1"]==1].drop(columns=["SEXISTAT1"], axis=1).pivot_table(index=["ITTER107"], columns=["Causa iniziale di morte - European Short List"], values='Value')
causa_morte_series_f = causa_morte[causa_morte["SEXISTAT1"]==2].drop(columns=["SEXISTAT1"], axis=1).pivot_table(index=["ITTER107"], columns=["Causa iniziale di morte - European Short List"], values='Value')
causa_morte_series_tot = causa_morte[causa_morte["SEXISTAT1"]==9].drop(columns=["SEXISTAT1"], axis=1).pivot_table(index=["ITTER107"], columns=["Causa iniziale di morte - European Short List"], values='Value')

morti_resp_path = os.path.join("ISTAT_DATA", "Deaths(#), Diseases of the respiratory system, Total.csv")
morti_resp = pd.read_csv(morti_resp_path).set_index("index")

##########################################################################################################################################
##########################################   DROPPING USELESS - ADDING PROCAPITE COLUMNS   ###############################################
##########################################################################################################################################

df_regioni_today = df_regioni_today.drop(columns=['data', 'stato', 'codice_regione', 'denominazione_regione', 'lat', 'long', 'note_it', 'note_en', 'codice_storico', 'giorno'], axis=1)
df_province_today = df_province_today.drop(columns=['data', 'stato', 'codice_regione', 'denominazione_regione', 'codice_provincia', 'denominazione_provincia', 'sigla_provincia', 'lat', 'lon', 'note_it', 'note_en', 'giorno'], axis=1)

df_regioni_today['ricoverati_con_sintomi_procapite'] = df_regioni_today['ricoverati_con_sintomi']/pop_series_reg['Popolazione_ETA1_Total']
df_regioni_today['terapia_intensiva_procapite'] = df_regioni_today['terapia_intensiva']/pop_series_reg['Popolazione_ETA1_Total']
df_regioni_today['totale_ospedalizzati_procapite'] = df_regioni_today['totale_ospedalizzati']/pop_series_reg['Popolazione_ETA1_Total']
df_regioni_today['isolamento_domiciliare_procapite'] = df_regioni_today['isolamento_domiciliare']/pop_series_reg['Popolazione_ETA1_Total']
df_regioni_today['dimessi_guariti_procapite'] = df_regioni_today['dimessi_guariti']/pop_series_reg['Popolazione_ETA1_Total']
df_regioni_today['deceduti_procapite'] = df_regioni_today['deceduti']/pop_series_reg['Popolazione_ETA1_Total']
df_regioni_today['totale_casi_procapite'] = df_regioni_today['totale_casi']/pop_series_reg['Popolazione_ETA1_Total']
df_regioni_today['tamponi_procapite'] = df_regioni_today['tamponi']/pop_series_reg['Popolazione_ETA1_Total']
df_regioni_today['casi_testati_procapite'] = df_regioni_today['casi_testati']/pop_series_reg['Popolazione_ETA1_Total']

df_province_today['totale_casi_procapite'] = df_province_today['totale_casi']/pop_series['Popolazione_ETA1_Total']

##########################################################################################################################################

st.markdown("# HIGHEST CORRELATION VALUES")
st.markdown("## REGIONI")

df_total=df_regioni_today.join(pop_series_reg)

for idx, df in enumerate([smokers_series, air_reg_series, imprese_series, bmi_series_reg, pov_fam_series_reg, pov_ind_series_reg]):
    df_total = df_total.join(df)

c = df_total.corr('pearson').abs()
s = c.unstack()
so = s.sort_values(kind="quicksort").to_frame().rename(columns={0:"pearson"})

for corr_type in ['kendall', 'spearman']:
    c = df_total.corr(corr_type).abs()
    s = c.unstack()
    tmp = s.sort_values(kind="quicksort").to_frame().rename(columns={0:corr_type})
    so = so.join(tmp)
so = so.reset_index()

so = so[so["level_0"]!=so["level_1"]]
# so = so[so['pearson']<=0.9999]
# so = so[so['kendall']<=0.9999]
# so = so[so['spearman']<=0.9999]
so = so[so["level_0"].isin(df_regioni_today.columns)]
so = so[~so["level_1"].isin(df_regioni_today.columns)]

so['ordered-cols'] = so.apply(lambda x: '-'.join(sorted([x['level_0'],x['level_1']])),axis=1)
dataCorr = so.drop_duplicates(['ordered-cols'])
dataCorr.drop(['ordered-cols'], axis=1, inplace=True)
dataCorr.to_csv(os.path.join("ISTAT_DATA", "correlations.csv"))

##########################################################################################################################################
#########################################################   VISUALIZATION   ##############################################################
##########################################################################################################################################
st.markdown("# DEATHS GRAPH VISUALIZER")
morti_resp.at[0,'Covid'] = df_regioni_today['deceduti'].sum()

fig = go.Figure(data=[
    go.Bar(name='Malattie Sistema Respiratorio', x=morti_resp['Year'], y=morti_resp['Value']),
    go.Bar(name='COVID-19', x=morti_resp['Year'], y=morti_resp['Covid'])
])
fig.update_layout(barmode='stack')
st.plotly_chart(fig,use_container_width=True)

st.markdown("# CORRELATION VISUALIZER")

st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
corr_filter = st.radio("Correlation Type",["Pearson","Kendall","Spearman"])

st.markdown("## REGIONI")
st.write('Popolazione')
join_and_plot(df_regioni_today, pop_series_reg)

st.write('Fumatori')
join_and_plot(df_regioni_today, smokers_series)

st.write('Inquinamento')
join_and_plot(df_regioni_today, air_reg_series)

st.write('Imprese')
join_and_plot(df_regioni_today, imprese_series)

st.write('BMI')
join_and_plot(df_regioni_today, bmi_series_reg)

st.write('Povertà Familiare')
join_and_plot(df_regioni_today, pov_fam_series_reg)

st.write('Povertà Individuale')
join_and_plot(df_regioni_today, pov_ind_series_reg)


##########################################################################################################################################

st.markdown("## PROVINCE")
st.write('Popolazione')
join_and_plot(df_province_today, pop_series)

st.write('Inquinamento')
join_and_plot(df_province_today, air_series.drop(columns=['denominazione_regione', "COMUNI", "CODICE PROVINCIA", "NUTS3_regione"]))