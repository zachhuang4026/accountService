**Creating Docker Container for Account Service**
```bash
docker run -p 5001:5001 --name AccountService -e POSTGRES_PASSWORD=secret_password -d postgres:15.1-alpine
docker exec -it AccountService /bin/sh
apk add postgresql-dev gcc python3-dev py3-pip musl-dev
pip install flask
pip install psycopg2 # https://github.com/psycopg/psycopg2/issues/684#issuecomment-392015532
mkdir /accountService

# Create Account DB [Postgres Shell]
psql --username postgres
create database accounts;
exit

# Run Python script to setup ACCOUNT_DIM table with default values
cd /accountService
python3 db_setup.py
```

https://luppeng.wordpress.com/2020/02/28/install-and-start-postgresql-on-alpine-linux/
