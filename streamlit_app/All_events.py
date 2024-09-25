import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout='wide')

# setting a html for cards
cards_html = '''
    <div style="display:flex; flex-wrap:wrap; justify-content:center">
        {cards}
    </div>
'''

# card_html = '''
#     <div style="background-color:#f9f9f9; padding:10px; border-radius:10px;
#                 box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); margin:10px;
#                 width:300px; height:300px">
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
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{
            transform: scale(1.05);
            box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
        }}
        .date {{
            margin-top: auto;
            font-weight: bold;
        }}
    </style>
    <div class="card">
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
                                  date = pd.to_datetime(event['startDateTime']).date())
    return cards


# function to display the data of cards received as cards
def display_as_cards(cards):
    st.markdown(cards_html.format(cards=cards), unsafe_allow_html=True)

# Function to render event details
def show_event_details(event_id):
    # Here, you can fetch the event details based on event_id
    # For now, just displaying the ID as a placeholder
    st.header(f"Details for Event ID: {event_id}")


st.header('All Events')

server_url = 'http://127.0.0.1:5000'
events_endpoint = server_url + '/event_data'

response = requests.get(events_endpoint)

if response.status_code == 200:
    response_obj = response.json()
    events = response_obj['data']
    cards = convert_json_to_cards(events)
    display_as_cards(cards)

else:
    print('Error. Couldn\'t load.')

