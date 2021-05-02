import streamlit as st
import geopandas
import matplotlib.pyplot as plt

percentage = st.sidebar.slider('Percentage',0, 100, 50)
order = st.sidebar.selectbox('Town order', ('Population', 'Density', 'Area'))
descending = st.sidebar.checkbox('Descending', value=True)

order_map = {
        'Population':'PB_TOWN_16',
        'Density': 'density',
        'Area': 'PB_TOWN__3'
    }

variable_name = order_map[order]

nh = geopandas.read_file('New_Hampshire_Political_Boundaries/New_Hampshire_Political_Boundaries.shp')

@st.cache(suppress_st_warning=True)
def calculate_constants():
    """Returns total state population and calculates pop density for each town
    """
    nh['density'] = nh['PB_TOWN_16'] / nh['PB_TOWN__3']
    return nh.PB_TOWN_16.sum()

TOTAL_POPULATION = calculate_constants()

threshold = percentage / 100.0

population_threshold = threshold * TOTAL_POPULATION
running_total = 0.0

nh['shaded_town'] = 0

for i, row in nh.sort_values(variable_name, ascending = not descending).iterrows():
    running_total += row.PB_TOWN_16
    if running_total > population_threshold:
        break
    nh.loc[nh.pbpNAME == row.pbpNAME, 'shaded_town'] = 1

nh['coords'] = nh['geometry'].apply(lambda x: x.representative_point().coords[:])
nh['coords'] = [coords[0] for coords in nh['coords']]

fig, ax = plt.subplots(1,1, figsize=(11,17))
nh.plot(column='shaded_town', ax=ax)
plt.title(f"{percentage}% of New Hampshire's population", fontsize=14)

for idx, row in nh[nh.shaded_town == 1].iterrows():
    plt.annotate(text=row.pbpNAME, xy=row['coords'],horizontalalignment='center', fontsize=4)

plt.tick_params(left=False,
                bottom=False,
                labelleft=False,
                labelbottom=False)

st.pyplot(fig)