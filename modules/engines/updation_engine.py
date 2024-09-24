import threading
import string

import requests
import numpy as np
import pandas as pd
from pandas import json_normalize
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

# Download stopwords and other necessary corpora if you haven't done so (For first time use. Run the nltk_downloader.py file in the terminal to perform this action)
# nltk.download('stopwords')  
# nltk.download('wordnet')  # For lemmatizer
# nltk.download('omw-1.4')  # For lemmatizer if needed


# API urls to be used
# events_data_url = 'http://127.0.0.1:5000/event_data'  # API from local server (inside the api_request_test_folder), for events' data
users_data_url = 'http://127.0.0.1:5000/user_data'  # API from local server (inside the api_request_test_folder), for order history data
server_url = 'https://9d0a-157-119-213-251.ngrok-free.app'  # remote server url
events_data_url = server_url + '/api/bm/events' # remote server endpoint to obtain the data of all events
# users_data_url = server_url + '/api/bm/GetOrderUser'  # remote server url to obtain the data of order history


# creating a thread lock mechanism to protect files while they are being updated
update_lock = threading.Lock()


# setting some nltk initialisers and variables
stopwords_eng = set(stopwords.words("english"))
punct = set(string.punctuation)
lemma = WordNetLemmatizer()


# some global variables to be kept in-memory
retrieved_combined_content_similarity_df = None # dataframe format of the combined content-similarity matrix
retrieved_item_similarity_df = None # dataframe format of the combined item-similarity matrix
retrieved_user_item_matrix_df = None    # dataframe format of the user-item matrix
retrieved_event_df = None   # dataframe that holds the data of all the events
retrieved_recommendable_events_list = None # a list that holds the event ids of the events that can be recommended
recommendable_events_info_list = None   # a list containing all the event data in the json respose format for each event












# function to perform text pre-processing
def clean(document):
  
  stopwords_removed = ' '.join([i for i in document.lower().split() if i not in stopwords_eng])   # removing stopwords
  punctuations_removed = ''.join(ch for ch in stopwords_removed if ch not in punct)   # removing punctuations
  normalized = ' '.join(lemma.lemmatize(word) for word in punctuations_removed.split())   # converting words to their root form
  return normalized




# function to update the in-memory dataframe of all the events
def update_event_df():

    # getting data of all events from the events_data_url
    response = requests.get(events_data_url)
    if response.status_code == 200:
        json_obj = response.json()
    else:
        error_message = "error: " + str(response.status_code)
        return error_message
        
    df = json_normalize(json_obj['data']) # converting the complex json data format to a simpler tabular format
    event_df = df[['id', 'title', 'description', 'price', 'status', 'organizerId', 'startDateTime', 'endDateTime', 'createdOn', 'venue.city', 'venue.state', 'venue.country']].copy()
    event_df = event_df.dropna() # removing any event that has these values as null (not possible, but kept to avoid unwanted errors)
    event_df = event_df[event_df['status'] == 1]

    # editing df
    event_df['CombinedDescription'] = ((event_df['title'] + ' ') * 2 + event_df['description']).apply(lambda x: clean(x))    # CombinedDescription column holds the title and description words (preprocessed using clean function)

    # converting the datetime columns to datetime format
    event_df['startDateTime'] = pd.to_datetime(event_df['startDateTime'])
    event_df['endDateTime'] = pd.to_datetime(event_df['endDateTime'])
    event_df['Duration'] = (event_df['endDateTime'] - event_df['startDateTime']).dt.total_seconds() / 3600  # Duration column hold the length of the event

    today_datetime = pd.to_datetime('today')
    event_df['createdOn'] = pd.to_datetime(event_df['createdOn'])   # we have to use modifiedOn instead of createdOn (but current data have it configured to null, so createdOn is being used as a subitute till the response is configured correctly)
    event_df['Recency'] = (today_datetime - event_df['createdOn'])  # Recency column holds datetime values w.r.t the recency of the creation of the event
    
    # creating and saving a list of the events that can be recommended (only the events in the future are saved in this list)
    recommendable_events_list = event_df['id'][event_df['startDateTime'] > today_datetime].tolist()

    # extracting the info of the events that can be recommended, in the json format to be saved and returned as response when required
    recommendable_json_obj = [event_info for event_info in json_obj['data'] if event_info['id'] in recommendable_events_list]

    # saving the new calculations to the global variables and the json file
    with update_lock:

        global retrieved_event_df
        retrieved_event_df = event_df

        global retrieved_recommendable_events_list
        retrieved_recommendable_events_list = recommendable_events_list

        global recommendable_events_info_list
        recommendable_events_info_list = recommendable_json_obj




# function to get title and description similarity matrix
def title_desc_similarity():

    # using tfidf to calculate similarity among events based on the combined description
    # we can improve recommendations by using more advanced models like word embeddings, BERT etc., in future, which will be able to understand the meaning of the title and description
    tfidf = TfidfVectorizer(analyzer='word', ngram_range=(1, 5), min_df=0.0, stop_words='english')
    tfidf_matrix = tfidf.fit_transform(retrieved_event_df['CombinedDescription'])
    desc_similarity_matrix = linear_kernel(tfidf_matrix, tfidf_matrix)

    return desc_similarity_matrix




# function to get price similarity matrix
def price_similarity():

    price_arr = np.array(retrieved_event_df['price'])
    num_prices = len(price_arr)
    price_similarity_matrix = np.zeros((num_prices, num_prices))

    min_price = np.min(price_arr)
    max_price = np.max(price_arr)
    diff_price_min_max = max_price - min_price

    for i in range(num_prices):
        for j in range(i, num_prices):
            diff = abs(price_arr[i] - price_arr[j]) # calculating the absoute difference b/w the price of 2 events
            norm_val = 1 - (diff / (diff_price_min_max))    # normalizing the absolute difference
            price_similarity_matrix [i, j] = price_similarity_matrix [j, i] = norm_val

    return price_similarity_matrix




#function to get duration similarity matrix
def duration_similarity():

    duration_arr = np.array(retrieved_event_df['Duration'])
    num_durations = len(duration_arr)
    duration_similarity_matrix = np.zeros((num_durations, num_durations))

    min_duration = np.min(duration_arr)
    max_duration = np.max(duration_arr)
    diff_duration_min_max = max_duration - min_duration

    for i in range(num_durations):
        for j in range(i, num_durations):
            diff = abs(duration_arr[i] - duration_arr[j])   # calculating the abslute difference in durations of 2 events
            norm_val = 1 - (diff / diff_duration_min_max)   # normalizing the absolute difference
            duration_similarity_matrix [i, j] = duration_similarity_matrix [j, i] = norm_val
    
    return duration_similarity_matrix




# function to get venue similarity matrix
def venue_similarity():

    ohenc = OneHotEncoder()

    city_encoded = ohenc.fit_transform(retrieved_event_df[['venue.city']])  # encoding the city values
    state_encoded = ohenc.fit_transform(retrieved_event_df[['venue.state']])    # encoding the state values
    country_encoded = ohenc.fit_transform(retrieved_event_df[['venue.country']])    # encoding the country values

    # cosine_similarites for venue components
    venue_city_similarity = linear_kernel(city_encoded, city_encoded)   # matrix representing similarity in city
    venue_state_similarity = linear_kernel(state_encoded, state_encoded)    # matrix representing similarity in state
    venue_country_similarity = linear_kernel(country_encoded, country_encoded)  # matrix representing similarity in country

    weight_country = 0.55
    weight_state = 0.35
    weight_city = 0.1

    venue_similarity_matrix = (
        (weight_country * venue_country_similarity) + 
        (weight_state * venue_state_similarity) +
        (weight_city * venue_city_similarity)
    )

    return venue_similarity_matrix




# function to get organizer similarity matrix
def organizer_similarity():

    ohenc = OneHotEncoder()

    organizer_encoded = ohenc.fit_transform(retrieved_event_df[['organizerId']])    # encoding the organizer ids

    organizer_similarity_matrix = linear_kernel(organizer_encoded)  # matrix representing similarity in organizer

    return organizer_similarity_matrix




# function to get date similarity
def date_similarity():
    
    dates = retrieved_event_df['startDateTime']
    
    num_dates = len(dates)
    date_similarity_matrix = np.zeros((num_dates, num_dates))
    
    min_date = dates.min()
    max_date = dates.max()
    diff_date_min_max = (max_date - min_date).days
    
    if(diff_date_min_max == 0.0):
        diff_date_min_max = 1.0 

    for i in range(num_dates):
        for j in range(i, num_dates):
            diff = abs(dates[i] - dates[j]).days
            norm_val = 1 - (diff / (diff_date_min_max))
            date_similarity_matrix [i, j] = date_similarity_matrix [j, i] = norm_val
                            
    return date_similarity_matrix




# function to get time(hour) similarity
def time_similarity():
    
    hour_arr = np.array(retrieved_event_df['startDateTime'].dt.hour)
    
    num_times = len(hour_arr)
    hour_similarity_matrix = np.zeros((num_times, num_times))
            
    for i in range(num_times):
        for j in range(i, num_times):
            diff = abs(hour_arr[i] - hour_arr[j])
            norm_val = 1 - (diff / 23.0)
            hour_similarity_matrix [i, j] = hour_similarity_matrix [j, i] = norm_val
                            
    return hour_similarity_matrix











#function to create a new similartiy matrix from the all-events api response
def update_content_recommendation_matrix():

    # first updating the dataframe holding the events
    update_event_df()

    #calculation of new similarity matrix
    title_desc_similarity_matrix = title_desc_similarity()
    price_similarity_matrix = price_similarity()
    duration_similarity_matrix = duration_similarity()
    venue_similarity_matrix = venue_similarity()
    organizer_similarity_matrix = organizer_similarity()
    date_similarity_matrix = date_similarity()
    time_similarity_matrix = time_similarity()
    # these different types of similarities can also be used separately in future

    weight_desc = 0.55  # weighted over half (for now) so that even the combined weight of other attributes does not override the description similarity
    weight_price = 0.05
    weight_duration = 0.025
    weight_venue = 0.2
    weight_organizer = 0.025
    weight_date = 0.075
    weight_time = 0.075  # we have separated date and time similarity to allow the flexibility to assign different weightage to these attributes
    # in future these weights can be assigned dynamically based on users' preferences about certain criterias (like price etc.)
    # the attributes that the user selects/enters can be used to change these weights dynamically so that the recommendations are more personalised

    combined_content_similarity_matrix = (
        (weight_desc * title_desc_similarity_matrix) +
        (weight_price * price_similarity_matrix) +
        (weight_duration * duration_similarity_matrix) +
        (weight_venue * venue_similarity_matrix) +
        (weight_organizer * organizer_similarity_matrix) +
        (weight_date * date_similarity_matrix) +
        (weight_time * time_similarity_matrix)
    )

    # converting the similarity matrix to a dataframe for easier access and manipulation
    content_similarity_df = pd.DataFrame(combined_content_similarity_matrix, index=retrieved_event_df['id'], columns=retrieved_event_df['id'])

    # updating the memory with latest events and matrix
    with update_lock:

        global retrieved_combined_content_similarity_df
        retrieved_combined_content_similarity_df = content_similarity_df




# function to create a new user-item matrix using order history (GetOrderUser) api response
def update_user_item_matrix():

    # getting response from the past order details of users
    response = requests.get(users_data_url)
    if response.status_code == 200:
        user_json_obj = response.json()
    else:
        error_message = "error: " + str(response.status_code)
        return error_message

    # creation of the user-item matrix
    user_df = pd.DataFrame(user_json_obj).rename(columns={'eventId': 'event_id', 'userId': 'user_id'})
    user_item_matrix = pd.pivot_table(user_df, index='user_id', columns='event_id', aggfunc='size', fill_value=0)
    user_item_matrix = pd.DataFrame(
        np.where(user_item_matrix > 0, 1, 0),
        index=user_item_matrix.index,
        columns=user_item_matrix.columns
    )

    # calculating cosine similarity between items and storing the matrix as a dataframe for easier access and manipulation
    item_similarity_matrix = cosine_similarity(user_item_matrix.T)
    item_similarity_df = pd.DataFrame(item_similarity_matrix, index=user_item_matrix.columns, columns=user_item_matrix.columns)

    # saving the new results to the global variables
    with update_lock:

        global retrieved_user_item_matrix_df
        retrieved_user_item_matrix_df = user_item_matrix

        global retrieved_item_similarity_df
        retrieved_item_similarity_df = item_similarity_df