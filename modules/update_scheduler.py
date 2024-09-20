import threading

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




# handling periodic updates of the similarity matrix saved
def periodic_update():

    print('Updating recommendation matrices and files...')
    try:
        updater.update_content_recommendation_matrix()  # updating the content recommendation matrix
        print('Content based matrix updated successfully!')

        updater.update_user_item_matrix()   # updating the user-item matrix
        print('User Item matrix updated successfully!')

        update_events_list()    # updating the recommendable events list from the json file
        print("Upcoming published events' info list updated successfully!")

    except Exception as e:
        print(f'Failed to update: {str(e)}')