Install:

```sh
pip install fastapi uvicorn
```

Launch server

```sh
uvicorn MyVoyager.voyager_api.main:app --host 0.0.0.0 --port 8000 --reload
```

Example of queries:

```sh
curl -X POST "http://localhost:8000/launch/galaxy-scrape"
curl -X POST "http://localhost:8000/launch/galaxy-scrape?dataset=my_data2"
```

TODO: add custom stages (custom_scrape et datamine-stage), add options (max-roles, delete, report)
