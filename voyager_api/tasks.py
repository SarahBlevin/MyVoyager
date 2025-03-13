import subprocess
import json
from pathlib import Path

# Dictionary to track running tasks
tasks = {}

def run_stage(task_id: str, stage: str, dataset: str, options: dict):
    """Execute a Voyager stage with the specified dataset and options, and store logs."""
    log_file = Path(f"voyager_api/logs/{task_id}.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    command = ["python", "main.py", "--dataset", dataset, stage]

    if options.get("delete"):
        command.append("--delete")
    if options.get("max_roles") is not None:
        command.extend(["--max-roles", str(options["max_roles"])])
    if stage == "datamine-stage":
        if not options.get("script_path"):
            return {"error": "Datamine requires a script_path"}
        command.extend(["--path", options["script_path"]])
        if options.get("options"):
            json_options = json.dumps(options["options"])  # Convert options to JSON string
            command.extend(["--options", json_options])
    if stage == "custom-scrape" and options.get("schema"):
        command.extend(["--schema", options["schema"]])  # Keep schema option

    with log_file.open("w") as log:
        process = subprocess.Popen(
            command,
            stdout=log, stderr=subprocess.STDOUT,
            #cwd="MyVoyager"  # Ensure it runs from the correct directory
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
    log_file = Path(f"voyager_api/logs/{task_id}.log")
    if not log_file.exists():
        return {"task_id": task_id, "error": "Log not found"}

    return {"task_id": task_id, "logs": log_file.read_text()}

def list_stages():
    """Return available Voyager stages."""
    return {
        "stages": [
            "galaxy-scrape", "custom-scrape", "extract-role-metadata", "clone",
            "extract-git-metadata", "extract-structural-models",
            "extract-structural-diffs", "datamine-stage"
        ]
    }
