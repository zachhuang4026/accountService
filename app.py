from flask import Flask, Response, json, jsonify, request, redirect, url_for
import psycopg2
import uuid
import time

app = Flask(__name__)

app.config['DEBUG'] = False

def db_query(query, fetch_results=False, db='accounts'):
    try:
        rows = None
        conn = psycopg2.connect(f"dbname={db} user='postgres' host='localhost' password='secret_password'")
        cursor = conn.cursor()
        cursor.execute(query)
        if fetch_results:
            rows = cursor.fetchall() # cursor.rowcount
            schema = cursor.description
            column_names = [col[0] for col in schema]
            rows = [dict(zip(column_names, r)) for r in rows] # Return result as list of dict        
        conn.commit()
        conn.close()
        return rows
    except:
        raise


@app.route('/')
def heartbeat():
    status_code = 200
    response = {'code': status_code,
                'message': 'User microservice is online'}
    return jsonify(response), status_code

@app.route('/getAccount/<account_id>', methods=['GET'])
def getAccount(account_id):
    """
    Return account information, given account id
    """
    # ToDo - get account info from DB
    if app.config['DEBUG'] == True:
        status_code = 200
        response = {
            'account_id': 1234,
            'name': 'John Doe',
            'email': 'john.doe@gmail.com',
            'status_code': status_code
        }
    else:
        # ToDo - communicate with DB
        account_query = f'select account_id, name, email from ACCOUNT_DIM where account_id = {account_id}'
        db_response = db_query(account_query, fetch_results=True)
        if len(db_response) > 1:
            status_code = 500
            response = {'message': 'Database returned an unexpected number of records'}
        else:
            account_info = db_response[0]
            status_code = 200
            response = {'data': account_info, 'status_code': status_code}
    return jsonify(response), status_code

@app.route('/authenticate', methods=['POST'])
def authenticate():
    # ToDo - verify input format
    print(request.json.get('email'))
    print(request.json.get('password'))
    if None in [request.json.get('email'), request.json.get('password')]:
        # throw error
        status_code = 400
        message = 'Bad request. Did not contain email or password values in JSON'
        response = {'message': message, 'status_code': status_code}
        return jsonify(response), status_code
    else:
        email = request.json.get('email')
        password = request.json.get('password')

        if app.config['DEBUG'] == True:
            message = 'Authorization granted'
            status_code = 200
        else:
            # ToDo - probably should handle pw as hashes
            # ToDo - return JWT token?
            account_query = f"select account_id, email, password from ACCOUNT_DIM where email = '{email}'"
            db_response = db_query(account_query, fetch_results=True)
            if len(db_response) > 1:
                status_code = 500
                response = {'message': 'Database returned an unexpected number of records'}
            else:
                account_info = db_response[0]
                status_code = 200
                if account_info['email'] == email and account_info['password'] == password:
                    # Authenticated
                    response = {'message': 'User is authenticated', 'status_code': status_code}
                else:
                    response = {'message': 'Provided email/password do not match', 'status_code': status_code}
        
        return jsonify(response), status_code

@app.route('/createAccount', methods=['POST'])
def createAccount():
    # ToDo - verify input format 
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')

    if None in [request.json.get('name'), request.json.get('email'), request.json.get('password')]:
        # throw error
        status_code = 400
        response = {'message': 'Bad request. Did not contain required values in JSON', 'status_code': status_code}
    # ToDo - Try/Except communication with database
    # Check if email already in Database
    else:
        account_query = f"select account_id from ACCOUNT_DIM where email = '{email}'"
        db_response = db_query(account_query, fetch_results=True)
        # Check if account already exists for email
        if len(db_response) != 0:
            status_code = 200
            message = 'Account already exists for the provided email'
            response = {'message': message, 'status_code': status_code}
            return jsonify(response), status_code
        
        # ToDo - UUID for account ID
        # account_id = uuid.uuid4().int
        # ToDo: determine best way to come up with unique account_id
        account_id = hash(email + str(time.time())) % 2147483647 # max int value
        account_info = f"({account_id}, '{name}', '{email}', '{password}', 'Active', False)"
        insert_sql = f'''
        INSERT INTO ACCOUNT_DIM (ACCOUNT_ID, NAME, EMAIL, PASSWORD, ACCOUNT_STATUS, IS_ADMIN)
        VALUES
        {account_info};
        '''
        try:
            db_query(insert_sql)
            status_code = 200
            response = {'message': 'Account successfully created', 'status_code': status_code}
        except:
            status_code = 500
            response = {'message': 'Error creating account', 'status_code': status_code}

    return jsonify(response), status_code  

@app.route('/deleteAccount', methods=['POST'])
def deleteAccount():
    # ToDo - verify input format 
    account_id = request.json.get('account_id')
    if account_id is None:
        status_code = 400
        response = {'message': 'Bad request. Did not contain account_id values in JSON', 'status_code': status_code}
    else:
        delete_sql = f'delete from account_dim where account_id = {account_id};'
        try:
            db_query(delete_sql)
            status_code = 200
            response = {'message': 'Account successfully deleted', 'status_code': status_code}
        except:
            status_code = 500
            response = {'message': 'Error deleting account', 'status_code': status_code}
    return jsonify(response), status_code

@app.route('/updateAccount', methods=['POST'])
def updateAccount():
    # ToDo - verify input format 
    print('in /updateAccount')
    account_id = request.json.get('account_id')
    update_params = request.json.get('data')
    print(update_params)
    if account_id is None:
        status_code = 400
        response = {'message': 'Bad request. Did not contain email or password values in JSON', 'status_code': status_code}
    else:
        # table_info_query = "select column_name, data_type from information_schema.columns where table_name = 'account_dim';"
        col_str = ''
        for k,v in update_params.items(): # ToDo - is hardcoding logic for creating sql best approach here?
            if k == 'account_id': # prevent updating of account_id
                pass
            if k in ['name', 'email', 'password', 'account_status']:
                col_str += f"{k} = '{v}',"
            else:
                col_str += f"{k} = {v},"
        col_str = col_str[:-1] # remove traililng comma
        print(col_str)

        update_sql = f'''
        update account_dim
        set {col_str}
        where account_id = {account_id}
        '''
        try:
            db_query(update_sql)
            status_code = 200
            response = {'message': 'Account information successfully updated', 'status_code': status_code}
        except:
            status_code = 500
            response = {'message': 'Error deleting account', 'status_code': status_code}
    return jsonify(response), status_code

app.run(host='0.0.0.0', port=5001)