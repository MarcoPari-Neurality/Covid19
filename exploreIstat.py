import os
import streamlit as st
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

from utils import get_dataset, check_ds_istat, linear_reg, pretty_colors

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

def traces_punti_e_trend(x_data, y_data, idx, hovertemplate, text, name='data'):
           
    line_x, line_y, r_value, mape = linear_reg(x_data, y_data)

    trace_line = go.Scatter(
                        x=line_x,
                        y=line_y,
                        mode='lines',
                        hovertemplate = f"Trend:<br><b>R^2</b> : {str(round((r_value**2)*100, 2))}% <br><b>MAPE</b> : {str(round(mape, 2))}%  <extra></extra>",
                        legendgroup='group'+str(idx),
                        showlegend =False,
                        marker=go.scatter.Marker(color=pretty_colors[idx]))
    
    trace_markers = go.Scatter(
                        x=x_data, 
                        y=y_data,
                        mode='markers',
                        hovertemplate = hovertemplate,
                        text=text,
                        name=name,
                        legendgroup='group'+str(idx),
                        marker=go.scatter.Marker(color=pretty_colors[idx]))
    return trace_line, trace_markers

codici_regioni = ["ITG2", "ITG1", "ITF6", "ITF5", "ITF4", "ITF3", "ITF2", "ITF1", "ITE4", "ITE3", "ITE2", "ITE1", "ITD5", "ITC3", "ITD4", "ITD3", "ITD1", "ITD2", "ITC4", "ITC2", "ITC1"]

df_province, df_regioni, smokers_series, imprese_series, air_series  = get_dataset(date.today())

norm_data = st.checkbox("Normalize data")

smokers_series = smokers_series.drop(index=["2", "3", "6", "7", "8", "9", "IT", "ITC", "ITCD", "ITD", "ITDA", "ITE", "ITF", "ITFG", "ITG"])

imprese_reg_series = imprese_series.loc[smokers_series.index.array,:]

air_reg_series = air_series.drop(columns=["CODICE PROVINCIA", "COMUNI", "denominazione_regione"]).pivot_table(index='NUTS3_regione').drop(index="IT")

df_regioni_today = df_regioni[df_regioni["data"] == df_regioni["data"].max()]

df_province_today = df_province[df_province["data"] == df_province["data"].max()]

cols = [c for c in df_regioni_today.columns if 'Popolazione' in c or 'NUTS3' in c]
pop_series_reg = df_regioni_today[cols].set_index('NUTS3')

cols = [c for c in df_province_today.columns if 'Popolazione' in c or 'NUTS3' in c]
pop_series = df_province_today[cols].set_index('NUTS3')


cols = [c for c in df_regioni_today.columns if not 'Popolazione' in c]
df_regioni_today = df_regioni_today[cols].set_index("NUTS3")

cols = [c for c in df_province_today.columns if not 'Popolazione' in c]
df_province_today = df_province_today[cols].set_index("NUTS3")

if not norm_data:
    st.write(smokers_series)
    #st.write(pop_series_reg['Popolazione_ETA1_Total'])
    #st.write(smokers_series.multiply(pop_series_reg['Popolazione_ETA1_Total']/100, axis=0))
    #marco()


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
    malati = malati[malati["MISURA_AVQ"]=="HSC"] if norm_data else malati[malati["MISURA_AVQ"]=="THV"]
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
    bmi_reg = bmi_reg[bmi_reg["MISURA_AVQ"]=="HSC"] if norm_data else bmi_reg[bmi_reg["MISURA_AVQ"]=="THV"]
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

#df_regioni_today = df_regioni_today.drop(columns=['data', 'stato', 'codice_regione', 'denominazione_regione', 'lat', 'long', 'note_it', 'note_en', 'codice_storico', 'giorno', 'suscettibili'], axis=1)
#df_province_today = df_province_today.drop(columns=['data', 'stato', 'codice_regione', 'denominazione_regione', 'codice_provincia', 'denominazione_provincia', 'sigla_provincia', 'lat', 'lon', 'note_it', 'note_en', 'giorno'], axis=1)

if norm_data:
    df_regioni_today['ricoverati_con_sintomi'] = df_regioni_today['ricoverati_con_sintomi']/pop_series_reg['Popolazione_ETA1_Total']
    df_regioni_today['terapia_intensiva'] = df_regioni_today['terapia_intensiva']/pop_series_reg['Popolazione_ETA1_Total']
    df_regioni_today['totale_ospedalizzati'] = df_regioni_today['totale_ospedalizzati']/pop_series_reg['Popolazione_ETA1_Total']
    df_regioni_today['isolamento_domiciliare'] = df_regioni_today['isolamento_domiciliare']/pop_series_reg['Popolazione_ETA1_Total']
    df_regioni_today['dimessi_guariti'] = df_regioni_today['dimessi_guariti']/pop_series_reg['Popolazione_ETA1_Total']
    df_regioni_today['deceduti'] = df_regioni_today['deceduti']/pop_series_reg['Popolazione_ETA1_Total']
    df_regioni_today['totale_casi'] = df_regioni_today['totale_casi']/pop_series_reg['Popolazione_ETA1_Total']
    df_regioni_today['tamponi'] = df_regioni_today['tamponi']/pop_series_reg['Popolazione_ETA1_Total']
    df_regioni_today['casi_testati'] = df_regioni_today['casi_testati']/pop_series_reg['Popolazione_ETA1_Total']
    df_regioni_today['deceduti'] = df_regioni_today['deceduti']/pop_series_reg['Popolazione_ETA1_Total']
    df_regioni_today['dimessi_guariti'] = df_regioni_today['dimessi_guariti']/pop_series_reg['Popolazione_ETA1_Total']

    df_province_today['totale_casi_procapite'] = df_province_today['totale_casi']/pop_series['Popolazione_ETA1_Total']

pop_series_reg['Popolazione_ETA1_71-100+'] = pop_series_reg['Popolazione_ETA1_71-80'] + pop_series_reg['Popolazione_ETA1_81-90'] + pop_series_reg['Popolazione_ETA1_91-100+']

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

st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
corr_vis = st.radio("Correlation Visualization", ['Table', 'Heatmaps'])



'''
grafico contagi su pm10

'''


fig = go.Figure()
fig2 = go.Figure()
filtered_province_today = df_province[df_province["data"] == df_province["data"].max()].set_index('NUTS3')

filtered_province_today = filtered_province_today.drop(columns=[x for x in filtered_province_today.columns if not x in ["totale_casi", "Popolazione_ETA1_Total", "denominazione_provincia"]]).join(air_series, rsuffix='_other').drop(columns=['denominazione_regione', "COMUNI", "NUTS3_regione", "CODICE PROVINCIA"])
all_columns = [x for x in filtered_province_today.columns if "PM10" in x ]



prov_data = (filtered_province_today["totale_casi"]/filtered_province_today["Popolazione_ETA1_Total"]).rename('totale_casi_procapite')*100

prov_data = pd.concat([filtered_province_today.denominazione_provincia, prov_data, filtered_province_today[all_columns[0]], filtered_province_today[all_columns[1]]], axis=1)

prov_data_zero = prov_data.drop(prov_data[all_columns[0]][prov_data[all_columns[0]] == 0].index)

line, markers = traces_punti_e_trend(prov_data_zero.totale_casi_procapite, prov_data_zero[all_columns[0]], 0, "<b>%{text}</b><br>Casi Positivi procapite confermati: %{x:.3f}%<br>Giorni sopra il limite consigliato: %{y}<extra></extra>", prov_data_zero.denominazione_provincia)
fig.add_trace(line)
fig.add_trace(markers)

prov_data_one = prov_data.drop(prov_data[all_columns[1]][prov_data[all_columns[1]] == 0].index)

line, markers = traces_punti_e_trend(prov_data_one.totale_casi_procapite, prov_data_one[all_columns[1]], 0, "<b>%{text}</b><br>Casi Positivi procapite confermati: %{x:.3f}%<br>Media Annuale PM10: %{y}<extra></extra>", prov_data_one.denominazione_provincia)
fig2.add_trace(line)
fig2.add_trace(markers)

fig.add_trace(go.Scatter(
            x=np.arange(start=0, stop=2, step=0.1),
            y=[35,]*20,
            mode='lines',
            showlegend =False,
            hovertemplate='Limite di giorni sopra limite consigliati<extra></extra>')
)
fig.update_layout(
    title = "Inquinamento Aria (giorni con PM10 superiore al limite consigliato) / Casi positivi COVID",
    )
fig.update_xaxes(title_text='Contagi Procapite')
fig.update_yaxes(title_text='Giorni al di sopra del limite consigliato - 50 μg/m^3')
st.plotly_chart(fig,use_container_width=True)

fig2.add_trace(go.Scatter(
            x=np.arange(start=0, stop=2, step=0.1),
            y=[40,]*20,
            mode='lines',
            showlegend =False,
            hovertemplate='Limite di emissioni annuali consigliato<extra></extra>')
)
fig2.update_layout(
    title = "Inquinamento Aria (valore annuale medio) PM10 / Casi positivi COVID",
    )
fig2.update_xaxes(title_text='Contagi Procapite')
fig2.update_yaxes(title_text='Valore medio annuale [μg/m^3]')
st.plotly_chart(fig2,use_container_width=True)

##########################################################################################################################################
'''
grafico pm10 decessi/contagi

'''
fig = go.Figure()
fig2 = go.Figure()
filtered_regioni_today = df_regioni[df_regioni["data"] == df_regioni["data"].max()].set_index('NUTS3')

filtered_regioni_today = filtered_regioni_today.drop(columns=[x for x in filtered_regioni_today.columns if not x in ["deceduti", "totale_casi", "denominazione_regione"]]).join(air_reg_series, rsuffix='_other')
all_columns = [x for x in filtered_regioni_today.columns if "PM10" in x ]



prov_data = (filtered_regioni_today["deceduti"]/filtered_regioni_today["totale_casi"]).rename('decessi_su_totale_casi')*100

prov_data = pd.concat([filtered_regioni_today.denominazione_regione, prov_data, filtered_regioni_today[all_columns[0]], filtered_regioni_today[all_columns[1]]], axis=1)

prov_data_zero = prov_data.drop(prov_data[all_columns[0]][prov_data[all_columns[0]] == 0].index)

line, markers = traces_punti_e_trend(prov_data_zero.decessi_su_totale_casi, prov_data_zero[all_columns[0]], 0, "<b>%{text}</b><br>Decessi su Casi positivi confermati: %{x:.2f}%<br>Giorni sopra il limite consigliato: %{y}<extra></extra>", prov_data_zero.denominazione_regione)
fig.add_trace(line)
fig.add_trace(markers)

prov_data_one = prov_data.drop(prov_data[all_columns[1]][prov_data[all_columns[1]] == 0].index)

line, markers = traces_punti_e_trend(prov_data_one.decessi_su_totale_casi, prov_data_one[all_columns[1]], 0, "<b>%{text}</b><br>Decessi su Casi Positivi confermati: %{x:.2f}%<br>Media Annuale PM10: %{y}<extra></extra>", prov_data_one.denominazione_regione)
fig2.add_trace(line)
fig2.add_trace(markers)

fig.add_trace(go.Scatter(
            x=np.arange(start=0, stop=20, step=1),
            y=[35,]*20,
            mode='lines',
            showlegend =False,
            hovertemplate='Limite di giorni sopra limite consigliati<extra></extra>')
)
fig.update_layout(
    title = "Inquinamento Aria (giorni con PM10 superiore al limite consigliato) / Decessi per COVID",
    )
fig.update_xaxes(title_text='Decessi su Casi Positivi')
fig.update_yaxes(title_text='Giorni al di sopra del limite consigliato - 50 μg/m^3')
st.plotly_chart(fig,use_container_width=True)

fig2.add_trace(go.Scatter(
            x=np.arange(start=0, stop=20, step=1),
            y=[40,]*20,
            mode='lines',
            showlegend =False,
            hovertemplate='Limite di emissioni annuali consigliato<extra></extra>')
)
fig2.update_layout(
    title = "Inquinamento Aria (valore annuale medio) PM10 / Decessi per COVID",
    )
fig2.update_xaxes(title_text='Decessi su Casi Positivi')
fig2.update_yaxes(title_text='Valore medio annuale [μg/m^3]')
st.plotly_chart(fig2,use_container_width=True)

##########################################################################################################################################
'''
grafico decessi/contagi su 60+
'''
fig = go.Figure()
fig2 = go.Figure()
filtered_regioni_today = df_regioni[df_regioni["data"] == df_regioni["data"].max()].set_index('NUTS3')

filtered_regioni_today['Popolazione_ETA1_61-100+'] = filtered_regioni_today['Popolazione_ETA1_61-70']  + filtered_regioni_today['Popolazione_ETA1_71-80'] + filtered_regioni_today['Popolazione_ETA1_81-90'] + filtered_regioni_today['Popolazione_ETA1_91-100+']
filtered_regioni_today = filtered_regioni_today.drop(columns=[x for x in filtered_regioni_today.columns if not x in ["deceduti", "totale_casi", "Popolazione_ETA1_61-100+", "Popolazione_ETA1_Total", "denominazione_regione"]])
prov_data = (filtered_regioni_today["deceduti"]/filtered_regioni_today["totale_casi"]).rename('decessi_su_totale_casi')*100

prov_data = pd.concat([filtered_regioni_today.denominazione_regione, prov_data, filtered_regioni_today["Popolazione_ETA1_61-100+"].div(filtered_regioni_today["Popolazione_ETA1_Total"],axis=0).rename("pop_rischio")*100], axis=1)

line, markers = traces_punti_e_trend(prov_data.decessi_su_totale_casi, prov_data["pop_rischio"], 0, "<b>%{text}</b><br>Decessi su casi positivi confermati: %{x:.2f}%<br>Percentuale popolazione a rischio: %{y:.2f}%<extra></extra>", prov_data.denominazione_regione)
fig.add_trace(line)
fig.add_trace(markers)

fig.update_layout(
    title = "Rapporto decessi su numero di contagi rispetto a popolazione età avanzata",
    )
fig.update_xaxes(title_text='Decessi su Casi positivi')
fig.update_yaxes(title_text='Percentuale popolazione età avanzata (60+ anni)')
st.plotly_chart(fig,use_container_width=True)


##########################################################################################################################################
'''
grafico %fumreg con decessi/contagi
'''
fig = go.Figure()
fig2 = go.Figure()
filtered_regioni_today = df_regioni[df_regioni["data"] == df_regioni["data"].max()].set_index('NUTS3')

filtered_regioni_today = filtered_regioni_today.drop(columns=[x for x in filtered_regioni_today.columns if not x in ["deceduti", "totale_casi", "denominazione_regione", "Fumatori_Tipo dato_fumatori"]]).join(smokers_series, rsuffix='_other')

prov_data = (filtered_regioni_today["deceduti"]/filtered_regioni_today["totale_casi"]).rename('decessi_su_totale_casi')*100
prov_data = pd.concat([filtered_regioni_today.denominazione_regione, prov_data, filtered_regioni_today["Fumatori_Tipo dato_fumatori"] ], axis=1)

line, markers = traces_punti_e_trend(prov_data.decessi_su_totale_casi, prov_data["Fumatori_Tipo dato_fumatori"], 0, "<b>%{text}</b><br>Decessi su casi positivi confermati: %{x:.2f}%<br>Percentuale fumatori: %{y:.2f}%<extra></extra>", prov_data.denominazione_regione)
fig.add_trace(line)
fig.add_trace(markers)

fig.update_layout(
    title = "Rapporto decessi su numero di contagi rispetto a presenza fumatori",
    )
fig.update_xaxes(title_text='Decessi su Casi positivi')
fig.update_yaxes(title_text='Percentuale fumatori')
st.plotly_chart(fig,use_container_width=True)

##########################################################################################################################################
#########################################################   DATA ANALYSIS   ##############################################################
##########################################################################################################################################

if corr_vis == 'Table':
    st.markdown("# HIGHEST CORRELATION VALUES")
    st.markdown("## REGIONI")

    if norm_data:
        imprese_reg_series = imprese_reg_series.div(pop_series_reg['Popolazione_ETA1_Total'], axis=0)
        pop_series_reg = pop_series_reg.div(pop_series_reg['Popolazione_ETA1_Total'], axis=0)
    # st.write(df_regioni_today.at['ITF1', 'terapia_intensiva'])
    # marco()
    df_total=df_regioni_today.join(pop_series_reg)
    
    for idx, df in enumerate([smokers_series, air_reg_series, imprese_reg_series, bmi_series_reg, pov_fam_series_reg, pov_ind_series_reg]):
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
    so = so[so["level_0"].isin(df_regioni_today.columns)]
    so = so[~so["level_1"].isin(df_regioni_today.columns)]

    so['ordered-cols'] = so.apply(lambda x: '-'.join(sorted([x['level_0'],x['level_1']])),axis=1)
    dataCorr = so.drop_duplicates(['ordered-cols'])
    dataCorr.drop(['ordered-cols'], axis=1, inplace=True)
    dataCorr.to_csv(os.path.join("ISTAT_DATA", "corr_reg.csv"))
    st.write(dataCorr)

else:

    st.markdown("# CORRELATION VISUALIZER")

    corr_filter = st.radio("Correlation Type",["Pearson","Kendall","Spearman"])

    st.markdown("## REGIONI")
    st.write('Popolazione')
    join_and_plot(df_regioni_today, pop_series_reg)

    st.write('Fumatori')
    join_and_plot(df_regioni_today, smokers_series)

    st.write('Inquinamento')
    join_and_plot(df_regioni_today, air_reg_series)

    st.write('Imprese')
    join_and_plot(df_regioni_today, imprese_reg_series)

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