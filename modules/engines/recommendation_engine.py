from engines import updation_engine as updater











# returning the list of events that are currently available (events which have not started yet)
def event_availability(recommendation_list):

    available_events_list = [event for event in recommendation_list if event in updater.retrieved_recommendable_events_list]
    return available_events_list




# checking if the user's data is present in the user-item matrix or not
def user_activeness(user_id):
    
    if user_id is None:
        return False

    if user_id not in updater.retrieved_user_item_matrix_df.index:
        return False
    
    return True




# checking whether the event has activity
def event_activeness(event_id):

    if event_id is None:
        return False
    
    if event_id not in updater.retrieved_user_item_matrix_df.columns:
        return False
    
    return True




# checking if the event's data is present in the dataframe of all events or not
def event_in_memory(event_id):

    if event_id is None:
        return False

    if not event_id in updater.retrieved_event_df['id'].values:
        return False
    
    return True











# function to return events in order: latest to oldest
def upcoming_events(event_id=None):

    response_dict = {}

    # if an event_id is passed, i.e., if we need to display the latest events in the context of some other event, we are ensuring that the same event is not repeated again
    upcoming_events_df = updater.retrieved_event_df[updater.retrieved_event_df['id'] != event_id].sort_values(by='Upcoming')
    upcoming_events_list = upcoming_events_df['id'].tolist()
    upcoming_available_events_list = event_availability(upcoming_events_list)

    if len(upcoming_available_events_list) <= 0:
        response_dict["label"] = "No upcoming events' data availale"
        response_dict["data"] = None

        return response_dict

    if event_id is not None:
        response_dict["label"] = "Upcoming events"
        response_dict["data"] = upcoming_available_events_list

    else:
        response_dict["label"] = "Upcoming events"
        response_dict["data"] = upcoming_available_events_list

    return response_dict



# function to return events in order: (most number of people interacted with) to (least number of people interacted with)
# because if 1 or 2 parties book the entire event or most number of seats, it should not be tagged as popular
def popular_events(event_id=None):

    response_dict = {}

    # if an event_id is passed, i.e., we want to get popular events in the context of another event, we ensure that the same event is not returned again
    popularity_scores = updater.retrieved_user_item_matrix_df.loc[:, updater.retrieved_user_item_matrix_df.columns != event_id].sum()
    # popularity_scores = popularity_scores[popularity_scores.values > 0.0] # we don't need to check this because we will only have those events in user-item matrix that have atleast 1 booking
    popular_events_list = popularity_scores.sort_values(ascending=False).index.tolist()
    popular_available_events_list = event_availability(popular_events_list)

    if len(popular_available_events_list) <= 0:
        response_dict["label"] = "No popular events' data availale"
        response_dict["data"] = None

        return response_dict

    if event_id is not None:
        response_dict["label"] = "Other popular users"
        response_dict["data"] = popular_available_events_list

    else:
        response_dict["label"] = "Popular events"
        response_dict["data"] = popular_available_events_list

    return response_dict




#function to get content based recommendations
def content_based_recommendations(event_id):

    response_dict = {}
    
    # finding similar events if the event is present in the dataframe, i.e., it has been considered for similarity calculation
    if event_in_memory(event_id):
        similarity_df_events = updater.retrieved_combined_content_similarity_df.loc[event_id]
        other_similar_events = similarity_df_events[similarity_df_events.index != event_id]
        content_based_similar_events_list = (
            other_similar_events.sort_values(ascending=False).index.tolist()
        )
        
        content_based_available_similar_events_list = event_availability(content_based_similar_events_list)

        if len(content_based_available_similar_events_list) > 0:
            response_dict["label"] = "Similar events"
            response_dict["data"] = content_based_available_similar_events_list

        else:
            response_dict["label"] = "Simiar events not available yet"
            response_dict["data"] = None

        return response_dict
    
    # returning latest events if the event is fairly new
    else:
        response_dict["label"] = "Simiar events not available yet"
        response_dict["data"] = None

        return response_dict




# function to get items users-also liked
def users_also_liked(event_id):

    response_dict = {}

    # finding similarly-liked events if event has some activity, hence in user-item matrix
    if event_activeness(event_id):
        similar_events = updater.retrieved_item_similarity_df.loc[event_id]
        similar_events = similar_events[similar_events.values > 0.0]
        other_similar_events = similar_events[similar_events.index != event_id]
        
        user_based_similar_events_list = (
            other_similar_events.sort_values(ascending=False).index.tolist()
        )

        user_based_available_similar_events_list = event_availability(user_based_similar_events_list)

        if len(user_based_available_similar_events_list) > 0:
            response_dict["label"] = "Users also liked"
            response_dict["data"] = user_based_available_similar_events_list

        else:
            response_dict["label"] = "No event available for users-also-liked"
            response_dict["data"] = None

        return response_dict
    
    # if the event has no activity yet, we return popular events
    else:
        response_dict["label"] = "No event avaiable for users-also-liked"
        response_dict["data"] = None

        return response_dict




#function to get collaborative recommendations
def collaborative_item_based_recommendations(user_id):

    response_dict = {}

    # finding events that are similar to our user's likes, based on interactivity of other users, if our user has past activity
    if user_activeness(user_id):
        user_items = updater.retrieved_user_item_matrix_df.loc[user_id]
        liked_items = user_items[user_items > 0].index
            
        similar_items_scores = updater.retrieved_item_similarity_df[liked_items].sum(axis=1) # aggregate similarity scores for liked items
        similar_items_scores = similar_items_scores[similar_items_scores > 0.0]
        
        uninteracted_items_scores = similar_items_scores[user_items == 0] # catching items not already interacted with by the user
        collaborative_item_based_recommended_event_list = (
            uninteracted_items_scores.sort_values(ascending=False).index.tolist()
        )
        
        collaborative_item_based_recommended_available_event_list = event_availability(collaborative_item_based_recommended_event_list)

        if len(collaborative_item_based_recommended_available_event_list) > 0:
            response_dict["label"] = "For you"
            response_dict["data"] = collaborative_item_based_recommended_available_event_list

        else:
            response_dict["label"] = "No events available for user"
            response_dict["data"] = None

        return response_dict
    
    # if our user has no past activity, we return the list of latest events, event though popular events suit this case better,
    # because the list of popular events must be already available to the user on the events listing page
    else:
        # response_dict = upcoming_events()
        response_dict["label"] = "No user activity"
        response_dict["data"] = None

        return response_dict