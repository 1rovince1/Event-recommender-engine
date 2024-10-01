import requests
import pandas as pd
import streamlit as st

import links

# setting the stremlit app's layout to a wider view
st.set_page_config(layout='wide')

# setting all the required API request links
app_url = 'http://127.0.0.1:8000'
other_similar_events_endpoint = app_url + '/api/bm/recommendations/similar_events?current_event_id={current_event_id}&max_recommendations={max_recommendations}'
events_also_liked_by_ohter_users_endpoint = app_url + '/api/bm/recommendations/users_also_liked?current_event_id={current_event_id}&max_recommendations={max_recommendations}'











# setting a html for cards
cards_html = '''
    <div style="display:flex; flex-wrap:wrap; justify-content:center">
        {cards}
    </div>
'''

# card_html = '''
#     <div style="background-color:#f9f9f9; padding:10px; border-radius:10px;
#                 box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); margin:10px;
#                 width:300px; height:430px">
#         <h3>{id}. {title}</h3>
#         <p><b>Description:</b> {description}</p>
#         <p><b>Date:</b> {date}</p>
#         <p><b>Time:</b> {time}</p>
#         <p><b>Duration:</b> {duration}</p>
#         <p><b>Organizer:</b> {organizer}</p>
#         <p><b>City:</b> {city}</p>
#         <p><b>Price:</b> {price}</p>
#     </div>
# '''

card_html = '''
    <style>
        .card {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            margin: 10px;
            width: 250px;
            height: 300px;
            cursor: pointer;
            transition: transform 0.1s, box-shadow 0.2s;
        }}
        .card:hover {{
            transform: scale(1.01);
            box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
        }}
        .date {{
            margin-top: auto;
            font-weight: bold;
        }}
    </style>
    <div class="card" onclick="window.location.href='?event_id={id}'">
        <h3>{id}. {title}</h3>
        <p><b>Description:</b> {description}</p>
        <p class="date"><b>Date:</b> {date}</p>
    </div>
'''


# converting the json data received to cards
def convert_json_to_cards(json_data):
    cards = ''
    for event in json_data:

        # cards += card_html.format(id = event['id'],
        #                           title = event['title'],
        #                           description = event['description'],
        #                           date = pd.to_datetime(event['startDateTime']).date(),
        #                           time = pd.to_datetime(event['startDateTime']).time(),
        #                           duration = (pd.to_datetime(event['endDateTime']) - pd.to_datetime(event['startDateTime'])),
        #                           organizer = event['organizerId'],
        #                           city = event['venue']['city'],
        #                           price = event['price'])

        # brief card format
        cards += card_html.format(id = event['id'],
                                  title = event['title'],
                                  description = event['description'],
                                  date = pd.to_datetime(event['startDateTime']).date(),)
    return cards


# function to display the data of cards received as cards
def display_as_cards(cards):
    st.markdown(cards_html.format(cards=cards), unsafe_allow_html=True)




events_endpoint = links.server_url
events_list = []
description_dict = {}
date_dict = {}


response = requests.get(events_endpoint)

if response.status_code == 200:
    response_obj = response.json()
    events = response_obj['data']

    for event in events:
          event_id = event['id']
          event_title = event['title']
          event_description = event['description']
          event_date = pd.to_datetime(event['startDateTime']).date()
          events_list.append(f'{event_id}. {event_title}')
          description_dict[event_id] = (event_description)
          date_dict[event_id] = event_date

else:
    st.write('Error. Couldn\'t load.')


selection = st.selectbox('Select event: ',
                        options = events_list,
                        index = None,
                        placeholder = '0')

if selection is not None:
    event_id = int(selection.split()[0][:-1])
    st.write(f'Description: {description_dict[event_id]}')
    st.write(f'Date: {date_dict[event_id]}')
else:
    event_id = 0
# event_id = st.text_input('Enter event id: ', value = 0)
# max_recommendations = st.text_input('Enter the maximum number of recommendations: ', value=3)
max_recommendations = 3




other_similar_events_endpoint = other_similar_events_endpoint.format(current_event_id = event_id, max_recommendations = max_recommendations)
response = requests.get(other_similar_events_endpoint)

if response.status_code == 200:

        data = response.json()
        events = data['data']
        if events is None:
            st.header("No similar events available yet")
        else:
            st.header(data['label'])
            cards = convert_json_to_cards(events)
            display_as_cards(cards)

else:

        st.write('Error. Couldn\'t load')






events_also_liked_by_ohter_users_endpoint = events_also_liked_by_ohter_users_endpoint.format(current_event_id = event_id, max_recommendations = max_recommendations)
response = requests.get(events_also_liked_by_ohter_users_endpoint)

if response.status_code == 200:

        data = response.json()
        events = data['data']
        if events is None:
            st.header("No users-also-liked data available")
        else:
            st.header(data['label'])
            cards = convert_json_to_cards(events)
            display_as_cards(cards)

else:

        st.write('Error. Couldn\'t load')