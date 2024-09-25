import threading
import time

from engines import updation_engine as updater


# creating a thread lock mechanism to protect files while they are being updated
update_lock = threading.Lock()











# creating some global variables to be used in the APIs
retrieved_recommendable_events_info = None
retrieved_events_list = None
retrieved_indices = None




# we create an events_list to hold the data of the events that can be recommended
# this is done to easily get the response info to be sent to the front-end.
def update_events_list():

    with update_lock:

        global retrieved_recommendable_events_info
        retrieved_recommendable_events_info = updater.recommendable_events_info_list

        global events_list
        events_list = retrieved_recommendable_events_info

        global indices
        indices = {event['id']: i for i, event in enumerate(events_list)}




# function to update the content similarity matrix
def update_content_similarity_matrix():

    try:

        content_based_updation_start_time = time.time()
        updater.update_content_recommendation_matrix()  # updating the content recommendation matrix
        content_based_updation_end_time = time.time()
        print(f'Content based matrix updated successfully! ({(content_based_updation_end_time - content_based_updation_start_time):.6f} seconds)')

    except Exception as e:

        content_based_updation_end_time = time.time()
        print(f'Failed to update content similarity matrix: {str(e)} ({(content_based_updation_end_time - content_based_updation_start_time):.6f} seconds)')




# function to update user-item matrix
def update_user_item_matrix():

    try:

        user_item_update_start_time = time.time()
        updater.update_user_item_matrix()   # updating the user-item matrix
        user_item_update_end_time = time.time()
        print(f'User Item matrix updated successfully! ({(user_item_update_end_time - user_item_update_start_time):.6f} seconds)')

    except Exception as e:

        user_item_update_end_time = time.time()
        print(f'Failed to update user-item matrix: {str(e)} ({(user_item_update_end_time - user_item_update_start_time):.6f} seconds)')




# function to update events' info list
def update_events_info_list():

    try:

        events_list_update_start_time = time.time()
        update_events_list()    # updating the recommendable events list from the json file
        events_list_update_end_time = time.time()
        print(f"Upcoming published events' info list updated successfully! ({(events_list_update_end_time - events_list_update_start_time):.6f} seconds)")

    except Exception as e:

        events_list_update_end_time = time.time()
        print(f'Failed to update events\' info list: {str(e)} ({(events_list_update_end_time - events_list_update_start_time):.6f} seconds)')




# handling periodic updates of the similarity matrix saved
def periodic_update():

    # calculating the time elapsed in updation
    updation_start_time = time.time()

    print('Updating recommendation matrices and files...')

    update_content_similarity_matrix()
    update_user_item_matrix()
    update_events_info_list()

    updation_end_time = time.time()
    print(f'Total time elapsed in updation = {(updation_end_time - updation_start_time):.6f} seconds')