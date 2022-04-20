import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import folium_static
from streamlit_option_menu import option_menu
import math
import requests
import json
from PIL import Image



@st.experimental_memo
def load_markers():
    # load in data markers
    df = pd.read_csv('cities.csv')
    df = df[df['state_name'] == "Indiana"]
    df['file_path'] = "pictures/" + df['id'].astype(str) + ".png"
    df['hit'] = False
    return df

#@st.experimental_memo(suppress_st_warning=True)
def create_map(markers):
    #m = folium.Map(location=[45.5236, -122.6750])
    # center on Liberty Bell
    m = folium.Map(location=[markers['latitude'].mean(), markers['longitude'].mean()], zoom_start=10)

    # add marker for Liberty Bell
    tooltip = "Liberty Bell"
    folium.Marker(
        [39.949610, -75.150282], popup="Liberty Bell", tooltip=tooltip
    ).add_to(m)

    for index, row in markers.iterrows():
        # add markers
        tooltip = row['id']
        lat = row['latitude']
        lng = row['longitude']
        #tooltip = marker['id'].values
        folium.Marker(
        [lat, lng], tooltip=tooltip
    ).add_to(m)

    # call to render Folium map in Streamlit
    # load map
    return m

@st.experimental_memo(suppress_st_warning=True)
def first_map_load(_marker_map):
    st.write("first map")
    folium_static(_marker_map)

def load_map(lat, lng, marker_map):
    # load map
    marker_map.location = [lat, lng]
    #marker_map.zoom_start = [40]
    #marker_map.fit_bounds(marker_map.get_bounds(), padding=(30, 30))
    #marker_map.update_loc[lat, lng]
    folium_static(marker_map)

def add_point_to_map(lat, lng, tooltip, marker_map):
    # add point to map
    folium.Marker(
        [lat, lng], tooltip=tooltip,
        icon=folium.Icon(icon="cloud"),
    ).add_to(marker_map)

def get_loc():
    # get user location
    res = requests.get('http://ip-api.com/json/')
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    #lat = location_data['lat']
    #lng = location_data['lon']

    # fort wayne
    lat = 41.093842
    lng = -85.139236
    your_loc = [lat, lng]
    return your_loc


# distance function
def get_distance(point1, point2):
    # convert lat and long to radians and use the law of cosines to calculate the distance in meters
    lat1_rad = point1[0] * math.pi / 180
    lat2_rad = point2[0] * math.pi / 180
    lon_delta_rad = (point2[1] - point1[1]) * math.pi / 180
    R = 6371e3 # radius of earth
    
    dist = np.arccos(np.sin(lat1_rad) * np.sin(lat2_rad) + np.cos(lat1_rad)* np.cos(lat2_rad) * np.cos(lon_delta_rad)) * R / 1609
    dist = int(dist)
    
    # check if distance is within 1 mile
    if dist < 10:
        return True, dist
    else:
        return False, dist

# STREAMLIT ----------------------------------
st.set_page_config(layout="wide")

if 'first_run' not in st.session_state:
    st.session_state['first_run'] = True

if 'hit_id' not in st.session_state:
    st.session_state['hit_id'] = ""

# load markers
markers = load_markers()
marker_map = create_map(markers)

choose = option_menu("... App", ["Home", "Location", "Badges",],
                         icons=['house', 'camera fill', 'book'],
                         menu_icon="app-indicator", default_index=0,
                         orientation="horizontal",
                         styles={
        "container": {"padding": "5!important", "background-color": "#e3e1e1"},
        "icon": {"color": "blue", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#a3d4f0"},
    }
    )

if choose == "Home":
    st.title("Welcome to the ... App!")

    st.header("Navigate to the Location page to display the map and earn new badges!")
 
elif choose == "Location":
   
    st.title("Markers")

    if st.session_state.first_run == True:
        first_map_load(marker_map)

    update_loc = st.button("Update your location")

    if update_loc:
        # refresh loc button pressed
        st.session_state.first_run = False
        coords = get_loc()
        lat = coords[0]
        lng = coords[1]
        tooltip = "YOU!"

        # add your point to the map
        add_point_to_map(lat, lng, tooltip, marker_map)
        load_map(lat, lng, marker_map)


        # check distance from yourself to each marker
        # iterate through df and check for distances
        check_dict = {}
        for index, row in markers.iterrows():
            marker = [row['latitude'], row['longitude']]
            within, dist = get_distance(coords, marker)
            check_dict[row['id']] = within
        
        # create dataframe of checks
        df_check = pd.DataFrame.from_dict(check_dict, orient='index', columns=['Check']).reset_index()
        df_check = df_check[df_check['Check'] == True]
        if len(df_check) > 0:
            hit_txt = "You have a new badge!"
            hit_bool = True

            # get badge where there is a hit
            new_badge_id = int(df_check['index'].iloc[0])
            new_badge = markers[markers['id'] == new_badge_id]

            # change the df where there was a hit
            st.session_state.hit_id = new_badge_id
        else:
            hit_txt = "Move closer to a target!"
            hit_bool = False
        

        st.header(hit_txt)
        if hit_bool == True:
            st.balloons()

elif choose == "Badges":
    st.header("View your current badges!")

    cols = st.columns(4)




    
    # sort df
    markers.loc[markers['id'] == st.session_state.hit_id, 'hit'] = True
    markers = markers.sort_values(by=['hit'], ascending=False)
    print(markers['hit'].values)


    for i in range(24):
        if markers.iloc[i]['hit'] == True:
            file_path = markers[markers['hit'] == True]['file_path'].item()
            print(file_path)

            image = Image.open(file_path)
            cols[0].image(image, caption=markers[markers['hit'] == True]['name'].item())
        cols[0].header("...")
        cols[1].header("...")
        cols[2].header("...")
        cols[3].header("...")
        i = i + 3