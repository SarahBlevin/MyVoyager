import sys
import os
import uuid
import json
from fastapi import FastAPI, BackgroundTasks, Query
from voyager_api.tasks import run_stage, get_status, get_logs, list_stages

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Voyager API is running"}

@app.post("/launch/{stage}")
def launch_stage(
    stage: str, 
    background_tasks: BackgroundTasks, 
    dataset: str = Query("default", description="Dataset name"),
    delete: bool = Query(False, description="Delete existing output"),
    max_roles: int = Query(None, alias="max-roles", description="Limit number of roles (only for scrape stages)"),
    script_path: str = Query(None, description="Path to datamine script (only for datamine)"),
    options: str = Query(None, description="Options as a string (e.g., '{\"param1\": \"value1\", \"param2\": 42}')")
):
    """Launch a Voyager pipeline stage asynchronously with options."""
    if stage not in list_stages()["stages"]:
        return {"error": "Invalid stage"}

    task_id = str(uuid.uuid4())
    parsed_options = {"delete": delete}

    # Directly pass the options as a string (no need to parse it as JSON)
    if options:
        try:
            parsed_options["options"] = json.loads(options)  # safely convert the string into a dictionary
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format in options"}
        
    if stage in ["galaxy-scrape", "custom-scrape"]:
        parsed_options["max_roles"] = max_roles
    if stage == "custom-scrape" and schema:
        parsed_options["schema"] = schema
    elif stage == "datamine-stage":
        if not script_path:
            return {"error": "Datamine requires a script_path"}
        parsed_options["script_path"] = script_path

    # Print to ensure the options are being passed correctly
    print(f"Launching stage: {stage} with options: {parsed_options}")

    background_tasks.add_task(run_stage, task_id, stage, dataset, parsed_options)
    return {"task_id": task_id, "stage": stage, "dataset": dataset, "options": parsed_options}

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
