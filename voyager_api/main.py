import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from voyager_api.tasks import run_stage, get_status, get_logs, list_stages  # Now it should work!

from fastapi import FastAPI, BackgroundTasks, Query
import uuid

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Voyager API is running"}

@app.post("/launch/{stage}")
def launch_stage(
    stage: str, 
    background_tasks: BackgroundTasks, 
    dataset: str = Query("default", description="Dataset name")
):
    """Launch a Voyager pipeline stage asynchronously with a specified dataset."""
    task_id = str(uuid.uuid4())
    background_tasks.add_task(run_stage, task_id, stage, dataset)
    return {"task_id": task_id, "stage": stage, "dataset": dataset}

@app.get("/status/{task_id}")
def status(task_id: str):
    """Get the status of a running stage."""
    return get_status(task_id)

@app.get("/logs/{task_id}")
def logs(task_id: str):
    """Retrieve logs of a task execution."""
    return get_logs(task_id)

@app.get("/stages")
def available_stages():
    """Return a list of available Voyager stages."""
    return list_stages()
