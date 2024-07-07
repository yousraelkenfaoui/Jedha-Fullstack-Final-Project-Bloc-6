# Importations

## Import Libraries
import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np

st.markdown("<h1 style='text-align: center;'>Work Related Injuries Dashboard</h1>", unsafe_allow_html=True)
st.markdown("""
Welcome to our project dashboard. Here are some data visualizations we created through the exploration of our dataset. The dataset used comes from Kaggle, specifically from the United States government data for 2020.
""")


## Import Dataset
#@st.cache_data
def load_data(nrows=None):
  data = pd.read_csv("ITA_OSHA_Combined.csv", nrows=nrows)
  return data

data=load_data()

## Checkbox
if st.checkbox('Show the dataset'):
  #st.subheader('dataset')
  st.write(data)


## Data Visualizations

# Accidents per sector

data['sectors_code'] = data['sectors_code'].astype(str)

# Agréger les données par sectors_code
dafw_per_sector = data.groupby("sectors_code").agg(
    total_dafw_cases=pd.NamedAgg(column='total_dafw_cases', aggfunc='sum'),
    description=pd.NamedAgg(column='description', aggfunc='first')
).reset_index()

# Créer le graphique
fig = px.bar(dafw_per_sector, 
             x='sectors_code', 
             y='total_dafw_cases', 
             labels={'sectors_code': 'Sector Code', 'total_dafw_cases': 'Total DAFW Cases'},
             title='DAFW Cases per Sector',
             color='total_dafw_cases', 
             color_continuous_scale='Viridis',
             hover_data={'description': True})  # Ajouter les descriptions dans les infobulles

fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))  # Ajouter une bordure aux barres
fig.update_layout(
    title={
        'text': "DAFW Cases per Sector",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 24}  # Taille du titre
    }
)

st.plotly_chart(fig)

# Accidents distribution

data_melted = data.melt(id_vars=['sectors_code','subsectors_code', 'annual_average_employees', 'establishment_type',
           'total_hours_worked', 'total_cases'], 
                        value_vars=['total_deaths','total_dafw_cases','total_djtr_cases','total_other_cases'], 
                        var_name='accident_type', 
                        value_name='count')

  
data_filtered = data_melted[data_melted['count'] == 1]

accident_counts = data_filtered['accident_type'].value_counts().reset_index()
accident_counts.columns = ['accident_type', 'count']

fig = px.pie(accident_counts, values='count', names='accident_type', title='Accidents Distribution')

fig.update_layout(
    title={
        'text': "Accidents Distribution",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 24} 
    }
)

st.plotly_chart(fig)

# Correlation matrix

columns=['annual_average_employees', 'establishment_type','total_hours_worked', 'total_deaths', 'total_dafw_cases', 
         'total_djtr_cases', 'total_other_cases', 'total_cases']

correlation_matrix = data[columns].corr()

fig_corr = go.Figure(data=go.Heatmap(
  z=correlation_matrix.values,
  x=correlation_matrix.columns,
  y=correlation_matrix.columns,
  colorscale='Viridis',
  showscale=True,
  text=np.round(correlation_matrix.values, 2),
  texttemplate="%{text}"
))

fig_corr.update_layout(
    title={
        'text': "Correlation Matrix",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 24}  
    },
    xaxis=dict(
        title='Variables',
        titlefont=dict(size=18),
        tickfont=dict(size=12)
    ),
    yaxis=dict(
        title='Variables',
        titlefont=dict(size=18),
        tickfont=dict(size=12)
    )
)

st.plotly_chart(fig_corr)



# Map of the Most Accident-Prone States

state_names = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}

data['description_state'] = data['state'].map(state_names)

# Agréger les données par état
accidents_per_state = data.groupby(['state', 'description_state'])['total_dafw_cases'].sum().reset_index()
accidents_per_state['hovertext'] = accidents_per_state['description_state'] + '<br>Total DAFW Cases: ' + accidents_per_state['total_dafw_cases'].astype(str)


fig = go.Figure(data=go.Choropleth(
    locations=accidents_per_state['state'],  
    z=accidents_per_state['total_dafw_cases'],  
    locationmode='USA-states',  
    colorscale='Viridis',  
    colorbar_title="Total DAFW Cases",  
    text=accidents_per_state['hovertext'], 
    hoverinfo='location+z+text'  
))
for i, row in accidents_per_state.iterrows():
    fig.add_trace(go.Scattergeo(
        locationmode='USA-states',
        locations=[row['state']],
        text=row['total_dafw_cases'],
        mode='text',
        textfont=dict(
            size=12,
            color='white'  
        ),
        showlegend=False
    ))

fig.update_layout(
    title={
        'text': 'Total DAFW Cases per State',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 24}  
    },
    geo=dict(
        scope='usa',
        projection=go.layout.geo.Projection(type='albers usa'),
        showland=True,
        landcolor='lightgray',
        subunitwidth=1,
        subunitcolor='black'
    ),
    height=700,  
    width=1000,  
)

st.plotly_chart(fig)




## Dropdown for selecting a state

accidents_per_state['state_display'] = accidents_per_state['state'] + ' - ' + accidents_per_state['description_state']

state_selected_display = st.selectbox("Select a state you want to see total DAFW cases:", accidents_per_state['state_display'].unique())

state_selected = state_selected_display.split(' - ')[0]

total_dafw_cases_selected_state = accidents_per_state[accidents_per_state['state'] == state_selected]['total_dafw_cases'].values[0]
st.write(f'Total DAFW Cases for {state_selected} ({state_names[state_selected]}): {total_dafw_cases_selected_state}')

## Dropdown for selecting a sector

data['sector_display'] = data['sectors_code'] + ' - ' + data['description']

sector_selected_display = st.selectbox('Select a sector you want to see total DAFW cases:', data['sector_display'].unique())

sector_selected = sector_selected_display.split(' - ')[0]

total_dafw_cases_selected_sector = data[data['sectors_code'] == sector_selected]['total_dafw_cases'].sum()
st.write(f'Total DAFW Cases for sector {sector_selected}: {total_dafw_cases_selected_sector}')


## Side bar 
st.sidebar.header("Build dashboards with Streamlit")
st.sidebar.markdown("""
    * [Load and showcase data](#load-and-showcase-data)
    * [Charts directly built with Streamlit](#simple-bar-chart-built-directly-with-streamlit)
    * [Charts built with Plotly](#simple-bar-chart-built-with-plotly)
    * [Input Data](#input-data)
""")
e = st.sidebar.empty()
e.write("")
st.sidebar.write("Made with 💖 by [Jedha](https://jedha.co)")
