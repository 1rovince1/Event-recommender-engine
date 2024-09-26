from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from apscheduler.schedulers.background import BackgroundScheduler

import update_scheduler as sch_update
from engines import recommendation_engine as recommender


# initialising app and scheduler
app = FastAPI()
scheduler = BackgroundScheduler()











@app.on_event('startup')
def scheduler_on():

    sch_update.periodic_update() # updating matrices just at the startup
    # scheduler.add_job(sch_update.periodic_update, 'interval', seconds=10)
    scheduler.add_job(sch_update.periodic_update, 'interval', minutes=30)
    scheduler.start()
    print('Scheduler started. Recommendation matrices and related files will be updated every 30 minutes.')




@app.on_event('shutdown')
def scheduler_off():

    scheduler.shutdown()
    print('Scheduler shutdown.')

# we might need to setup a log file for these status/info messages instead of printing in the console











# api endpoint to get popular events
@app.get("/api/bm/recommendations/popular_events", response_model=Dict[str,Any])
async def popular_events(
    max_recommendations: Optional[int] = Query(5, description="Number of recommendations required")):

    try:
        # calling the recommendation logic
        recommended_event_ids = recommender.popular_events()

        # getting the events info in the required response format from the events_list
        recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Popular events",
            "data" : recommended_events[:max_recommendations]
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")
    




# api endpoint to get recommended events for a user
@app.get("/api/bm/recommendations/user_recommendations", response_model=Dict[str,Any])
async def personal_recommendations_for_user(
    current_user_id: int = Query(..., description="User ID of the current user"),
    max_recommendations: Optional[int] = Query(5, description="Number of recommendations required")):

    try:
        if current_user_id is None:
            raise HTTPException(status_code=400, detail="Missing 'current_user_id' in request parameters.")

        # calling the recommendation logic
        recommended_event_ids = recommender.collaborative_item_based_recommendations(current_user_id)

        # getting the events info in the required response format from the events_list
        recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Events recommended for the user",
            "data" : recommended_events[:max_recommendations]
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")
    




# api endpoint to get similar events
@app.get("/api/bm/recommendations/similar_events", response_model=Dict[str,Any])
async def events_similar_to_this_event(
    current_event_id: int = Query(..., description="Event ID of the selected event"),
    max_recommendations: Optional[int] = Query(2, description="Number of recommendations required")):

    try:
        if current_event_id is None:
            raise HTTPException(status_code=400, detail="Missing 'current_event_id' in request parameters.")

        # calling the recommendation logic
        recommended_event_ids = recommender.content_based_recommendations(current_event_id)

        # getting the events info in the required response format from the events_list
        recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Similar events",
            "data" : recommended_events[:max_recommendations]
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")
    




# api endpoint to get users-also-liked events
@app.get("/api/bm/recommendations/users_also_liked", response_model=Dict[str,Any])
async def other_users_also_liked(
    current_event_id: int = Query(..., description="Event ID of the selected event"),
    max_recommendations: Optional[int] = Query(2, description="Number of recommendations required")):

    try:
        if current_event_id is None:
            raise HTTPException(status_code=400, detail="Missing 'current_event_id' in request parameters.")

        # calling the recommendation logic
        recommended_event_ids = recommender.users_also_liked(current_event_id)

        # getting the events info in the required response format from the events_list
        recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Users-also-liked events",
            "data" : recommended_events[:max_recommendations]
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")





# api endpoint to trigger update in similarity calculation
@app.get("/api/bm/recommendations/update_similarity", response_model=Dict[str,Any])
async def update_similarity_config(
    tit_des: Optional[float] = Query(55.0, description="Weight of title-description in similarity calculation"),
    pr: Optional[float] = Query(5.0, description="Weight of price in similarity calculation"),
    dur: Optional[float] = Query(2.5, description="Weight of duration in similarity calculation"),
    ven: Optional[float] = Query(20.0, description="Weight of venue in similarity calculation"),
    org: Optional[float] = Query(2.5, description="Weight of organizer in similarity calculation"),
    dat: Optional[float] = Query(7.5, description="Weight of date in similarity calculation"),
    tim: Optional[float] = Query(7.5, description="Weight of time in similarity calculation")):

    try:
        sch_update.customize_content_similarity_matrix(
            tit_des,
            pr,
            dur,
            ven,
            org,
            dat,
            tim
        )

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Customized configurations!"
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")