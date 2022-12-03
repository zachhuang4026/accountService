# Account Service

## Setup
**Creating Docker Container for Account Service**
```bash
docker run -p 5001:5001 --net ebay --ip 172.20.0.4 --name AccountService -e POSTGRES_PASSWORD=secret_password -d postgres:15.1-alpine
docker exec -it AccountService /bin/sh
apk add postgresql-dev gcc python3-dev py3-pip musl-dev
pip install flask
pip install psycopg2 # https://github.com/psycopg/psycopg2/issues/684#issuecomment-392015532
pip install requests

# Create Account DB [Postgres Shell]
psql --username postgres
create database accounts; # Enter accounts db via \c accounts
exit

# Run Python script to setup ACCOUNT_DIM table with default values
# Copy files from local to container: docker cp accountService AccountService:/.
cd /accountService
python3 db_setup.py
```

## Running Flask App
```bash
docker exec -it AccountService /bin/sh
cd accountService
python3 app.py
```

## Endpoints
| Endpoint                   | Description                                         | HTTP Method |
|----------------------------|-----------------------------------------------------|-------------|
| `/`                        | Heartbeat method to check if microservice is online | GET         |
| `/getAccount/<account_id>` | Return account information                          | GET         |
| `/authenticate`            | Verify email/password match DB                      | POST        |
| `/createAccount`           | Add new record to DB                                | POST        |
| `/deleteAccount`           | Delete record from DB                               | POST        |
| `/updateAccount`           | Update values for existing record in DB             | POST        |


## Testing
**Python `requests` Library**
```python
# While flask app is Running
>>> import requests
>>> response = requests.get('http://localhost:5001/')
>>> response.json
{'code': 200, 'message': 'User microservice is online'}
>>> account_info = {'name': 'Christian Pulisic', 'email': 'cp10@gmail.com', 'password': 'soccer'}
>>> response = requests.post('http://localhost:5001/createAccount', json=account_info)
>>> response.json()
{'message': 'Account successfully created', 'status_code': 200}
```

**Postman**
- Set POST input parameters using the Raw input for request body. https://stackoverflow.com/questions/39008071/send-post-data-via-raw-json-with-postman

## Database Credentials
- `ACCOUNT_DIM` table has been populated with the following identities for testing

| Username | Password | Is Admin? |
|----------|----------|-----------|
| `admin`  | `admin`  | True      |
| `user`   | `user`   | False     |

**4. Push Container to Docker Hub**
```bash
# Create image
docker commit 9816053b72a2 adamlim1/account_service
# Push image to Docker Hub
docker image push adamlim1/account_service
# Pull image
docker run -it -p 5001:5001 --net ebay --ip 172.20.0.4 --name AccountService adamlim1/account_service:latest
```