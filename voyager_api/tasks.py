import subprocess
from pathlib import Path

# Dictionary to track running tasks
tasks = {}

def run_stage(task_id: str, stage: str, dataset: str):
    """Execute a Voyager stage with the specified dataset and store logs."""
    log_file = Path(f"MyVoyager/voyager_api/logs/{task_id}.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with log_file.open("w") as log:
        process = subprocess.Popen(
            ["python", "main.py", "--dataset", dataset, stage],  # Pass dataset argument
            stdout=log, stderr=subprocess.STDOUT,
            cwd="MyVoyager"  # Ensure it runs from the correct directory
        )
        tasks[task_id] = process

def get_status(task_id: str):
    """Check the status of a running task."""
    process = tasks.get(task_id)
    if not process:
        return {"task_id": task_id, "status": "not found"}
    
    return {"task_id": task_id, "status": "running" if process.poll() is None else "completed"}

def get_logs(task_id: str):
    """Retrieve logs for a specific task."""
    log_file = Path(f"MyVoyager/voyager_api/logs/{task_id}.log")
    if not log_file.exists():
        return {"task_id": task_id, "error": "Log not found"}

    return {"task_id": task_id, "logs": log_file.read_text()}

def list_stages():
    """Return available Voyager stages."""
    return {
        "stages": [
            "galaxy-scrape", "extract-role-metadata", "clone",
            "extract-git-metadata", "extract-structural-models",
            "extract-structural-diffs"
        ]
    }
