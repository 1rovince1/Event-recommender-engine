import streamlit as st
import requests

tit_des = st.text_input('Enter weight of title and description: ', value = 55.0)
pr = st.text_input('Enter weight of event price: ', value = 5.0)
dur = st.text_input('Enter weight of event duration: ', value = 2.5)
ven = st.text_input('Enter weight of event venue: ', value = 20.0)
org = st.text_input('Enter weight of event organizer: ', value = 2.5)
dat = st.text_input('Enter weight of event date: ', value = 7.5)
tim = st.text_input('Enter weight of event time: ', value = 7.5)


if st.button('Customize'):
    customization_api_endpoint = f'http://127.0.0.1:8000/api/bm/recommendations/update_similarity?tit_des={tit_des}&pr={pr}&dur={dur}&ven={ven}&org={org}&dat={dat}&tim={tim}'

    response = requests.get(customization_api_endpoint)

    if response.status_code == 200:
        st.write(response.json())
    else:
        st.write('Error!')
