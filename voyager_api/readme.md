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
curl -X POST "http://localhost:8000/launch/galaxy-scrape?dataset=my_data&delete=true&max-roles=100"
curl -X POST "http://localhost:8090/launch/custom-scrape?dataset=my_data2&delete=false&max-roles=5&schema=test_schema.json"
curl -X POST "http://localhost:8090/launch/datamine-stage?dataset=my_data2&delete=false&script_path=/home/florent/Documents/Sarahcours/FISEA3/PROCOM/MyVoyager/pipeline/datamine/test1.py"
curl -X POST "http://localhost:8090/launch/datamine-stage" \
     -H "Content-Type: application/json" \
     -d '{
           "dataset": "my_data2",
           "delete": true,
           "script_path": "/home/florent/Documents/Sarahcours/FISEA3/PROCOM/MyVoyager/pipeline/datamine/test1.py",
           "options": {
               "num_modules": "11"
           }
         }'


```

TODO: add custom stages (custom_scrape et datamine-stage), add options (max-roles, delete, report)
