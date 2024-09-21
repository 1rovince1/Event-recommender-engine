import requests
import streamlit as st

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

card_html = '''
    <div style="background-color:#f9f9f9; padding:10px; border-radius:10px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); margin:10px;
                width:45%; height:300px">
        <h3>{title}</h3>
        <p><b>Description:</b> {description}</p>
        <p><b>Date:</b> {date}</p>
        <p><b>Price:</b> {price}</p>
    </div>
'''

st.title('Event recommendation engine')    
st.write('We currently have these features: ')
selection = st.selectbox('Functionalities',
                         options=['Popular events', 'Personal recommendations', 'Similar events', 'Liked by other users'],
                         index=None,
                         placeholder='Select an option...')


# converting the json data received to cards
def convert_json_to_cards(json_data):
    cards = ''
    for event in json_data:
        cards += card_html.format(title = event['title'],
                                  description = event['description'],
                                  date = event['startDateTime'],
                                  price = event['price'])
    return cards


# function to display the data of cards received as cards
def display_as_cards(cards):
    st.markdown(cards_html.format(cards=cards), unsafe_allow_html=True)











# beginning the selection logic

# displaying popular events
if selection == 'Popular events':

    max_recommendations = st.text_input('Enter the maximum number of recommendations: ', value=5)
    popular_events_endpoint = popular_events_endpoint.format(max_recommendations = max_recommendations)
    response = requests.get(popular_events_endpoint)

    if response.status_code == 200:

        data = response.json()
        events = data['data']
        cards = convert_json_to_cards(events)
        display_as_cards(cards)

    else:
        
        st.write('Error. Couldn\'t load')






# displaying personal recommendations for a user
elif selection == 'Personal recommendations':

    user_id = st.text_input('Enter user id: ')
    max_recommendations = st.text_input('Enter the maximum number of recommendations:', value=5)
    personal_recommendations_endpoint = personal_recommendations_endpoint.format(current_user_id = user_id, max_recommendations = max_recommendations)
    response = requests.get(personal_recommendations_endpoint)

    if response.status_code == 200:

        data = response.json()
        events = data['data']
        cards = convert_json_to_cards(events)
        display_as_cards(cards)

    else:

        st.write('Error. Couldn\'t load')






# displaying events similar to an event
elif selection == 'Similar events':

    event_id = st.text_input('Enter event id: ')
    max_recommendations = st.text_input('Enter the maximum number of recommendations: ', value=5)
    other_similar_events_endpoint = other_similar_events_endpoint.format(current_event_id = event_id, max_recommendations = max_recommendations)
    response = requests.get(other_similar_events_endpoint)

    if response.status_code == 200:

        data = response.json()
        events = data['data']
        cards = convert_json_to_cards(events)
        display_as_cards(cards)

    else:

        st.write('Error. Couldn\'t load')






# displaying events liked by other users
elif selection == 'Liked by other users':

    event_id = st.text_input('Enter event id: ')
    max_recommendations = st.text_input('Enter the maximum number of recommendations: ', value=5)
    events_also_liked_by_ohter_users_endpoint = events_also_liked_by_ohter_users_endpoint.format(current_event_id = event_id, max_recommendations = max_recommendations)
    response = requests.get(events_also_liked_by_ohter_users_endpoint)

    if response.status_code == 200:

        data = response.json()
        events = data['data']
        cards = convert_json_to_cards(events)
        display_as_cards(cards)

    else:

        st.write('Error. Couldn\'t load')