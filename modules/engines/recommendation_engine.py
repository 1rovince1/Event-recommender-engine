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
def latest_events(event_id=None):

    # if an event_id is passed, i.e., if we need to display the latest events in the context of some other event, we are ensuring that the same event is not repeated again
    latest_events_df = updater.retrieved_event_df[updater.retrieved_event_df['id'] != event_id].sort_values(by='recency')
    latest_events_list = latest_events_df['id'].tolist()
    latest_available_events_list = event_availability(latest_events_list)

    return latest_available_events_list



# function to return events in order: (most number of people interacted with) to (least number of people interacted with)
# because if 1 or 2 parties book the entire event or most number of seats, it should not be tagged as popular
def popular_events(event_id=None):

    # if an event_id is passed, i.e., we want to get popular events in the context of another event, we ensure that the same event is not returned again
    popularity_scores = updater.retrieved_user_item_matrix_df.loc[:, updater.retrieved_user_item_matrix_df.columns != event_id].sum()
    popular_events_list = popularity_scores.sort_values(ascending=False).index.tolist()
    popular_available_events_list = event_availability(popular_events_list)

    return popular_available_events_list




#function to get content based recommendations
def content_based_recommendations(event_id):
    
    # finding similar events if the event is present in the dataframe, i.e., it has been considered for similarity calculation
    if event_in_memory(event_id):
        similarity_df_events = updater.retrieved_combined_content_similarity_df.loc[event_id]
        other_similar_events = similarity_df_events[similarity_df_events.index != event_id]
        content_based_similar_events_list = (
            other_similar_events.sort_values(ascending=False).index.tolist()
        )
        
        content_based_available_similar_events_list = event_availability(content_based_similar_events_list)

        return content_based_available_similar_events_list
    
    # returning latest events if the event is fairly new
    else:
        latest_events_list = latest_events(event_id)
        return latest_events_list




# function to get items users-also liked
def users_also_liked(event_id):

    # finding similarly-liked events if event has some activity, hence in user-item matrix
    if event_activeness(event_id):
        similar_events = updater.retrieved_item_similarity_df.loc[event_id]
        other_similar_events = similar_events[similar_events.index != event_id]
        user_based_similar_events_list = (
            other_similar_events.sort_values(ascending=False).index.tolist()
        )

        user_based_available_similar_events_list = event_availability(user_based_similar_events_list)

        return user_based_available_similar_events_list
    
    # if the event has no activity yet, we return popular events
    else:
        popular_events_list = popular_events(event_id)
        return popular_events_list




#function to get collaborative recommendations
def collaborative_item_based_recommendations(user_id):

    # finding events that are similar to our user's likes, based on interactivity of other users, if our user has past activity
    if user_activeness(user_id):
        user_items = updater.retrieved_user_item_matrix_df.loc[user_id]
        liked_items = user_items[user_items > 0].index
            
        similar_items_scores = updater.retrieved_item_similarity_df[liked_items].sum(axis=1) # aggregate similarity scores for liked items
        
        uninteracted_items_scores = similar_items_scores[user_items == 0] # catching items not already interacted with by the user
        collaborative_item_based_recommended_event_list = (
            uninteracted_items_scores.sort_values(ascending=False).index.tolist()
        )
        
        collaborative_item_based_recommended_available_event_list = event_availability(collaborative_item_based_recommended_event_list)

        return collaborative_item_based_recommended_available_event_list
    
    # if our user has no past activity, we return the list of latest events (as the list of popular events must be already available to the user on the events listing page)
    else:
        latest_events_list = latest_events()
        return latest_events_list