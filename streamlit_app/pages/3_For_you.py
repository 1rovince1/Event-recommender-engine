import requests
import pandas as pd
import streamlit as st

# setting the stremlit app's layout to a wider view
st.set_page_config(layout='wide')

# setting all the required API request links
app_url = 'http://127.0.0.1:8000'
popular_events_endpoint = app_url + '/api/bm/recommendations/popular_events?max_recommendations={max_recommendations}'
personal_recommendations_endpoint = app_url + '/api/bm/recommendations/user_recommendations?current_user_id={current_user_id}&max_recommendations={max_recommendations}'
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






user_id = st.text_input('Enter user id: ', value = 0, placeholder = 0)
max_recommendations = st.text_input('Enter the maximum number of recommendations:', value=6)

if user_id is None:
    st.title('New user (Not logged in)')

else:

    personal_recommendations_endpoint = personal_recommendations_endpoint.format(current_user_id = user_id, max_recommendations = max_recommendations)
    response = requests.get(personal_recommendations_endpoint)

    if response.status_code == 200:

            data = response.json()
            events = data['data']
            if events is None:
                st.title("No recommedations available yet")
            else:
                st.title(data['label'])
                cards = convert_json_to_cards(events)
                display_as_cards(cards)

    else:

            st.write('Error. Couldn\'t load')