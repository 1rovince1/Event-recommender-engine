import streamlit as st
import requests
import importlib
from pages import similarity_weights as wconfig
# import re

# # Regex pattern to match weights
# pattern = r'(\w+)\s*=\s*([\d\.]+)'

# with open('similarity_weights.py', 'r') as file:
#     file_content = file.read()

# # Find all matches
# weights = re.findall(pattern, file_content)

# # Convert to a dictionary
# weights_dict = {name: float(value) for name, value in weights}

tit_des = st.text_input('Enter weight of title and description: ', value = wconfig.weight_title_description_of_event)
pr = st.text_input('Enter weight of event price: ', value = wconfig.weight_price_of_event)
dur = st.text_input('Enter weight of event duration: ', value = wconfig.weight_duration_of_event)
ven = st.text_input('Enter weight of event venue: ', value = wconfig.weight_venue_of_event)
org = st.text_input('Enter weight of event organizer: ', value = wconfig.weight_organizer_of_event)
dat = st.text_input('Enter weight of event date: ', value = wconfig.weight_date_of_event)
tim = st.text_input('Enter weight of event time: ', value = wconfig.weight_time_of_event)


if st.button('Customize'):
    customization_api_endpoint = f'http://127.0.0.1:8000/api/bm/recommendations/update_similarity?tit_des={tit_des}&pr={pr}&dur={dur}&ven={ven}&org={org}&dat={dat}&tim={tim}'

    response = requests.get(customization_api_endpoint)

    if response.status_code == 200:
        res = response.json()
        st.markdown('<p style="color: green;">Success!</p>', unsafe_allow_html=True)
        st.write(res['message'])

        new_config = '\n'.join([
            f"# adjustable weights:",

            f"weight_title_description_of_event = {tit_des}",
            f"weight_price_of_event = {pr}",
            f"weight_duration_of_event = {dur}",
            f"weight_venue_of_event = {ven}",
            f"weight_organizer_of_event = {org}",
            f"weight_date_of_event = {dat}",
            f"weight_time_of_event = {tim}",


            f"# default weights:",

            f"# weight_title_description_of_event = 55.0",
            f"# weight_price_of_event = 5.0",
            f"# weight_duration_of_event = 2.5",
            f"# weight_venue_of_event = 20.0",
            f"# weight_organizer_of_event = 2.5",
            f"# weight_date_of_event = 7.5",
            f"# weight_time_of_event = 7.5"
        ])

        with open('pages/similarity_weights.py', 'w') as file:
            file.write(new_config)

        importlib.reload(wconfig)

    else:
        st.write('Error!')


