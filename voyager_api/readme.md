## Installation

To install the necessary dependencies, run:

```sh
pip install fastapi uvicorn
```

## Launch the Server

Start the server by navigating to the Voyager directory and running:

```sh
cd path/to/Voyager
uvicorn voyager_api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Example API Requests

Here are some example `curl` commands to interact with the API. These examples are generic and can be adapted to different datasets, stages, and options.

### Launch Galaxy Scrape Stage

```sh
curl -X POST "http://localhost:8000/launch/galaxy-scrape"
curl -X POST "http://localhost:8000/launch/galaxy-scrape?dataset=your_dataset_name"
curl -X POST "http://localhost:8000/launch/galaxy-scrape?dataset=your_dataset_name&delete=true&max-roles=100"
```

### Launch Custom Scrape Stage

```sh
curl -X POST "http://localhost:8000/launch/custom-scrape?dataset=your_dataset_name&delete=false&max-roles=5&schema=your_schema.json"
```

### Launch Datamine Stage

```sh
curl -X POST "http://localhost:8000/launch/datamine-stage?dataset=your_dataset_name&delete=false&script_path=/path/to/your/script.py"
curl -X POST "http://localhost:8000/launch/datamine-stage?dataset=your_dataset_name&delete=true&script_path=/path/to/your/script.py&options=%7B%22num_modules%22%3A11%7D"
```

In the `options` field, pass options as a URL-encoded JSON string, such as `{"num_modules": 11}`.

### Parameters

- **`dataset`**: The name of the dataset you are processing (e.g., `your_dataset_name`).
- **`delete`**: A boolean flag to determine whether to delete existing output (`true` or `false`).
- **`max-roles`**: Optional, limits the number of roles (used in scrape stages).
- **`schema`**: The path to the schema file (for custom scrape).
- **`script_path`**: Path to the script to run (for the datamine stage).
- **`options`**: Optional, additional options passed as a URL-encoded JSON string (e.g., `{"num_modules": 11}`).
