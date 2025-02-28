import json
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from web.api.api_utils import recommending_pomodoro
router = APIRouter()

# File path for storing tasks
os.makedirs("data", exist_ok=True)
task_file = "data/time_management.json"


# Load existing tasks from file
def load_tasks():
    if os.path.exists(task_file):
        with open(task_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


# Save tasks to file
def save_tasks(tasks):
    with open(task_file, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)


# Function to find available time slot
def find_available_slot(estimated_hours, deadline):
    tasks = load_tasks()

    # Convert deadline to datetime
    deadline_dt = datetime.fromisoformat(deadline)

    # Check from now until the deadline for available slot
    current_time = datetime.now()

    while current_time + timedelta(hours=estimated_hours) <= deadline_dt:
        overlap = any(
            current_time < datetime.fromisoformat(task["scheduled_end"]) and
            (current_time + timedelta(hours=estimated_hours)) > datetime.fromisoformat(task["scheduled_start"])
            for task in tasks
        )

        if not overlap:
            return current_time.isoformat(), (current_time + timedelta(hours=estimated_hours)).isoformat()

        current_time += timedelta(hours=1)  # Move to next hour slot

    return None, None


class Task(BaseModel):
    task_name: str
    duration: int  # in minutes
    deadline: str  # ISO format: YYYY-MM-DDTHH:MM:SS


class PomodoroRequest(BaseModel):
    task: str
    duration: str


class ScheduleTask(BaseModel):
    task_name: str
    deadline: str
    estimated_time_hours: int


@router.post("/schedule_task")
def schedule_task(request: ScheduleTask):
    """
    Schedule a task before the given deadline.
    """
    scheduled_start, scheduled_end = find_available_slot(request.estimated_time_hours, request.deadline)

    if not scheduled_start:
        raise HTTPException(status_code=400, detail="No available time slot before deadline.")

    # Load tasks and add new task
    tasks = load_tasks()
    new_task = {
        "task_name": request.task_name,
        "scheduled_start": scheduled_start,
        "scheduled_end": scheduled_end,
        "deadline": request.deadline
    }

    tasks.append(new_task)
    save_tasks(tasks)

    return {"message": "Task scheduled successfully", "scheduled_start": scheduled_start,
            "scheduled_end": scheduled_end}


@router.get("/get_schedule")
def get_schedule():
    """
    Retrieve all scheduled tasks.
    """
    tasks = load_tasks()
    return {"tasks": tasks}


@router.post("/prioritize_tasks")
def prioritize_tasks(tasks: List[Task]):
    """
    Prioritizes tasks based on the earliest deadline and shorter duration.
    """
    try:
        # Convert deadline strings to datetime objects
        for task in tasks:
            task.deadline = datetime.fromisoformat(task.deadline)

        # Sort by (deadline, duration)
        prioritized_tasks = sorted(tasks, key=lambda t: (t.deadline, t.duration))

        # Add priority numbers
        result = [
            {"task_name": task.task_name, "deadline": task.deadline.isoformat(), "priority": index + 1}
            for index, task in enumerate(prioritized_tasks)
        ]

        return {"prioritized_tasks": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend_pomodoro")
def recommend_pomodoro(request: PomodoroRequest):
    """
    Generates a recommended Pomodoro study schedule.
    """

    response_text = recommending_pomodoro(request.task, request.duration)

    return {"message": response_text}

