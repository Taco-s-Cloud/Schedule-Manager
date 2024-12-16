# routers/schedules.py
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schedule import Schedule
from app.middleware.auth import verify_token
import base64

# Create a Blueprint for schedule routes
schedules_blueprint = Blueprint('schedules', __name__)

# PUB/SUB: Handle Pub/Sub messages
@schedules_blueprint.route("/schedules/pubsub", methods=["POST"])
def pubsub_handler():
    try:
        # Validate Pub/Sub message envelope
        envelope = request.get_json()
        if not envelope:
            return "Bad Request: Missing JSON", 400

        pubsub_message = envelope.get("message")
        if not pubsub_message:
            return "Bad Request: Missing 'message'", 400

        # Decode Pub/Sub message data
        data = base64.b64decode(pubsub_message.get("data", "")).decode("utf-8")
        print(f"Pub/Sub Message Received: {data}")

        # Extract additional Pub/Sub message attributes (optional)
        attributes = pubsub_message.get("attributes", {})
        print(f"Pub/Sub Message Attributes: {attributes}")

        # Example: Parse the data as JSON (if the message is a JSON string)
        parsed_data = None
        try:
            parsed_data = eval(data)  # Replace with json.loads(data) for secure parsing
            print(f"Parsed Data: {parsed_data}")
        except Exception as e:
            print(f"Error parsing Pub/Sub message: {e}")

        # Save to database (example)
        if parsed_data:
            db: Session = next(get_db())
            new_schedule = Schedule(
                user_id=parsed_data.get("user_id"),
                title=parsed_data.get("title"),
                description=parsed_data.get("description"),
                start_time=parsed_data.get("start_time"),
                end_time=parsed_data.get("end_time"),
                location=parsed_data.get("location"),
                reminder=int(parsed_data.get("reminder", 0)),
            )
            db.add(new_schedule)
            db.commit()
            db.refresh(new_schedule)
            print(f"New schedule added from Pub/Sub: {new_schedule.id}")

        return "Message processed", 200

    except Exception as e:
        print(f"Error processing Pub/Sub message: {e}")
        return jsonify({"error": str(e)}), 500

# GET: Retrieve all schedules
@schedules_blueprint.route("/schedules", methods=["GET"])
@verify_token
def get_schedules():
    try:
        db: Session = next(get_db())
        user_id = request.user_uid
        schedules = db.query(Schedule).filter(Schedule.user_id==user_id).all()
        #schedules = db.query(Schedule).all()
        schedule_list = [
            {
                "id": schedule.id, 
                "user_id": schedule.user_id,
                "title": schedule.title,
                "description": schedule.description,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
                "location": schedule.location,
                "reminder": str(schedule.reminder),
            }
            for schedule in schedules
        ]
        return jsonify(schedule_list), 200
    except Exception as e:
        print(f"Error retrieving schedules: {e}")
        return jsonify({"error": str(e)}), 500

# POST: Save a new schedule
@schedules_blueprint.route("/schedules", methods=["POST"])
@verify_token
def save_schedule():
    data = request.get_json()
    reminder = data.get('reminder')
    if reminder is not None:
        reminder = int(reminder)
    try:
        db: Session = next(get_db())
        new_schedule = Schedule(
            user_id=request.user_uid,
            title=data['title'],
            description=data.get('description'),
            start_time=data['start_time'],
            end_time=data['end_time'],
            location=data.get('location'),
            reminder=reminder
        )
        db.add(new_schedule)
        db.commit()
        db.refresh(new_schedule)
        return jsonify({"message": "Schedule saved", "schedule": data}), 201
    except Exception as e:
        print(f"Error saving schedule: {e}")
        return jsonify({"error": str(e)}), 500

# PUT: Update an existing schedule
@schedules_blueprint.route("/schedules/<int:schedule_id>", methods=["PUT"])
@verify_token
def update_schedule(schedule_id):
    data = request.get_json()
    try:
        db: Session = next(get_db())
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if schedule:
            schedule.title = data.get('title', schedule.title)
            schedule.description = data.get('description', schedule.description)
            schedule.start_time = data.get('start_time', schedule.start_time)
            schedule.end_time = data.get('end_time', schedule.end_time)
            schedule.location = data.get('location', schedule.location)
            schedule.reminder = data.get('reminder', schedule.reminder)
            db.commit()
            db.refresh(schedule)
            return jsonify({"message": "Schedule updated"}), 200
        else:
            return jsonify({"error": "Schedule not found"}), 404
    except Exception as e:
        print(f"Error updating schedule: {e}")
        return jsonify({"error": str(e)}), 500

# DELETE: Remove a schedule
@schedules_blueprint.route("/schedules/<int:schedule_id>", methods=["DELETE"])
@verify_token
def delete_schedule(schedule_id):
    try:
        db: Session = next(get_db())
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if schedule:
            db.delete(schedule)
            db.commit()
            return jsonify({"message": "Schedule deleted"}), 200
        else:
            return jsonify({"error": "Schedule not found"}), 404
    except Exception as e:
        print(f"Error deleting schedule: {e}")
        return jsonify({"error": str(e)}), 500

