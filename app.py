from flask import Flask, jsonify, request
import psycopg2
import time
import configparser

app = Flask(__name__)

app.config['DEBUG'] = True

config = configparser.ConfigParser()
config.read('account_config.ini')

def db_query(query, fetch_results=False, db='accounts'):
    """
    Helper function to execute SQL query on ACCOUNT_DIM table.
    The fetch_results parameter determines whether function should return 
    results from the query (e.g. SELECT statement) or just execute the query (e.g. INSERT/DELETE)
    """
    try:
        rows = None
        user = config['postgres']['user']
        host = config['postgres']['host']
        password = config['postgres']['password']
        conn = psycopg2.connect(f"dbname={db} user='{user}' host='{host}' password='{password}'")
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
    """
    Endpoint to check if microservice is online
    """
    status_code = 200
    response = {'code': status_code,
                'message': 'Account microservice is online'}
    return jsonify(response), status_code

@app.route('/getAccount/<account_id>', methods=['GET'])
def getAccount(account_id, DEBUG=False):
    """
    Provided account_id in query string, return account information.
    Throws error if > 1 record is found for provided account_id
    Output: {'data': {'account_id': account_id, 'name':name, 'email': email}, 'status_code': status_code}
    """
    # ToDo - get account info from DB
    if DEBUG == True:
        status_code = 200
        response = {
            'account_id': '1234',
            'name': 'John Doe',
            'email': 'john.doe@gmail.com',
            'status_code': status_code
        }
    else:
        # Communicate with DB
        account_query = f'''
        SELECT ACCOUNT_ID, NAME, EMAIL
        FROM ACCOUNT_DIM
        WHERE ACCOUNT_ID = '{account_id}'
        '''
        db_response = db_query(account_query, fetch_results=True)
        if len(db_response) != 1:
            status_code = 500
            response = {'message': 'Database returned an unexpected number of records', 'status_code': status_code}
        else:
            account_info = db_response[0]
            status_code = 200
            response = {'data': account_info, 'status_code': status_code}
    return jsonify(response), status_code

@app.route('/authenticate', methods=['POST'])
def authenticate(DEBUG=False):
    """
    Verifies provided email and password match record in DB
    Expected POST input format (JSON content type): {"email": email, "password": password}
    Output: {'message': message, 'status_code': status_code, 'data': {'account_id': account_id , 'is_admin':  is_admin}}
    """

    email = request.json.get('email')
    password = request.json.get('password')
    
    # If missing required POST parameters, throw error
    if None in [email, password]:
        status_code = 400
        response = {'message': 'Bad request. Did not contain email or password values in JSON', 'status_code': status_code}
    else:
        if DEBUG == True:
            status_code = 200
            response = {'message': 'Authorization granted', 'status_code': status_code}
        else:
            # ToDo - probably should handle pw as hashes
            # Get account info from email
            account_query = f"""
            SELECT ACCOUNT_ID, EMAIL, PASSWORD, ACCOUNT_STATUS, IS_ADMIN
            FROM ACCOUNT_DIM
            WHERE EMAIL = '{email}'"""
            
            db_response = db_query(account_query, fetch_results=True)

            if len(db_response) > 1:
                status_code = 500
                response = {'message': 'Database returned an unexpected number of records', 'status_code': status_code}
            elif len(db_response) == 0:
                status_code = 400
                response = {'message': 'Account not found in database', 'status_code': status_code}
            else:
                account_info = db_response[0]
                if account_info['account_status'] == 'Suspended':
                    status_code = 401
                    response = {'message': f'Account {account_info["account_id"]} is suspended. Login access denied', 'status_code': status_code}
                    return jsonify(response), status_code
                if account_info['email'] == email and account_info['password'] == password:
                    # Authenticated
                    status_code = 200
                    data = {'account_id':account_info['account_id'], 'is_admin': account_info['is_admin']}
                    response = {'message': f'Account {account_info["account_id"]} is authenticated', 'data': data, 'status_code': status_code}
                else:
                    status_code = 401
                    response = {'message': 'Provided email/password do not match', 'status_code': status_code}
        
        return jsonify(response), status_code

@app.route('/createAccount', methods=['POST'])
def createAccount():
    """
    Create new account in database.
    Expected Input: {'name': name, 'email': email, 'password': password}
    Output: {'message': message, 'status_code': status_code}
    """
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')

    # If missing required POST parameters, throw error
    if None in [name, email, password]:
        status_code = 400
        response = {'message': 'Bad request. Did not contain required values in JSON', 'status_code': status_code}
    else:
        # Check if account already exists for email
        account_query = f"""
        SELECT ACCOUNT_ID
        FROM ACCOUNT_DIM
        WHERE EMAIL = '{email}'
        """
        db_response = db_query(account_query, fetch_results=True)
        
        if len(db_response) != 0:
            status_code = 406
            response = {'message': 'Account already exists for the provided email', 'status_code': status_code}
            return jsonify(response), status_code
        
        # Populate values for account, insert into DB
        account_id = hash(email + str(time.time())) % 2147483647 # max int value
        account_info = f"('{account_id}', '{name}', '{email}', '{password}', 'Active', False)"
        insert_sql = f'''
        INSERT INTO ACCOUNT_DIM (ACCOUNT_ID, NAME, EMAIL, PASSWORD, ACCOUNT_STATUS, IS_ADMIN)
        VALUES {account_info};
        '''
        try:
            db_query(insert_sql)
            status_code = 201
            response = {'message': f'Account {account_id} successfully created', 'status_code': status_code}
        except:
            status_code = 500
            response = {'message': f'Error creating account {account_id}', 'status_code': status_code}

    return jsonify(response), status_code  

@app.route('/deleteAccount', methods=['POST'])
def deleteAccount():
    """
    Delete account from database.
    Input: {'account_id': account_id}
    Output: {'message': message, 'status_code': status_code}
    """
    account_id = request.json.get('account_id')
    # If missing required POST parameters, throw error
    if account_id is None:
        status_code = 400
        response = {'message': 'Bad request. Did not contain account_id values in JSON', 'status_code': status_code}
    else:
        delete_sql = f'''
        DELETE 
        FROM ACCOUNT_DIM 
        WHERE ACCOUNT_ID = '{account_id}';
        '''
        try:
            db_query(delete_sql)
            status_code = 200
            response = {'message': f'Account {account_id} successfully deleted', 'status_code': status_code}
        except:
            status_code = 500
            response = {'message': f'Error deleting account {account_id}', 'status_code': status_code}
    return jsonify(response), status_code

@app.route('/updateAccount', methods=['POST'])
def updateAccount():
    """
    Update information for existing account
    Input: {'account_id': 'xxx', 'data' : {'field1': 'xxx', ...}}
    Output: {'message': 'xxx', 'status_code': 'xxx'}
    """
    account_id = request.json.get('account_id')
    update_params = request.json.get('data')
    # If missing required POST parameters, throw error
    if account_id is None:
        status_code = 400
        response = {'message': 'Bad request. Did not contain email or password values in JSON', 'status_code': status_code}
        return jsonify(response), status_code
    
    # Check if user exists in DB
    check_exists_sql = f"""
    SELECT ACCOUNT_ID
    FROM ACCOUNT_DIM
    WHERE ACCOUNT_ID = '{account_id}'
    """
    rows = db_query(check_exists_sql, fetch_results=True)
    if len(rows) == 0:
        status_code = 404
        response = {'message': f'Account {account_id} does not exist in database', 'status_code': status_code}
        return jsonify(response), status_code
 
    # Create string of update logic 
    col_str = ''
    for k,v in update_params.items(): 
        if k == 'account_id': # prevent updating of account_id
            pass
        if k == 'is_admin': # No quotes needed around boolean field
            col_str += f"{k} = {v},"
        else:
            # Check if email already in DB and not current account; throw error if so 
            if k == 'email': 
                verify_email_sql = f"""
                SELECT ACCOUNT_ID
                FROM ACCOUNT_DIM
                WHERE EMAIL = '{v}'
                """
                rows = db_query(verify_email_sql, fetch_results=True)
                if (len(rows) > 1) or (len(rows) == 1 and rows[0]['account_id'] != account_id):
                    status_code = 500
                    response = {'message': f'Error updating account {account_id}. Account already exists for the provided email', 'status_code': status_code}
                    return jsonify(response), status_code
            col_str += f"{k} = '{v}',"
    
    col_str = col_str[:-1] # remove traililng comma. SQL string complete

    update_sql = f'''
    UPDATE ACCOUNT_DIM
    SET {col_str}
    WHERE ACCOUNT_ID = '{account_id}'
    '''
    try:
        db_query(update_sql)
        status_code = 200
        response = {'message': f'Information successfully updated for account {account_id}', 'status_code': status_code}
    except:
        status_code = 500
        response = {'message': f'Error updating account {account_id}', 'status_code': status_code}
    return jsonify(response), status_code

app.run(host='0.0.0.0', port=5001)