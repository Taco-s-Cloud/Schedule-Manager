# routers/schedules.py
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schedule import Schedule

# Create a Blueprint for schedule routes
schedules_blueprint = Blueprint('schedules', __name__)

# GET: Retrieve all schedules
@schedules_blueprint.route("/schedules", methods=["GET"])
def get_schedules():
    try:
        db: Session = next(get_db())
        schedules = db.query(Schedule).all()
        schedule_list = [
            {
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
def save_schedule():
    data = request.get_json()
    try:
        db: Session = next(get_db())
        new_schedule = Schedule(
            user_id=data['user_id'],
            title=data['title'],
            description=data.get('description'),
            start_time=data['start_time'],
            end_time=data['end_time'],
            location=data.get('location'),
            reminder=data.get('reminder')
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

