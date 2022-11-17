from flask import Flask, Response, json, jsonify, request
import psycopg2

app = Flask(__name__)

app.config['DEBUG'] = False

def db_query(query, db='accounts'):
    try:
        conn = psycopg2.connect(f"dbname={db} user='postgres' host='localhost' password='secret_password'")
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall() # cursor.rowcount
        conn.commit()
        conn.close()
        return rows
    except:
        print('issue with execution')


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
        account_query = f'select * from ACCOUNT_DIM where account_id = {account_id}'
        account_info = db_query(account_query)
        # Temp work around for returning response 
        response = {'account_id': account_id, 'name': account_info[0][1], 'email': account_info[0][2]}
        status_code = 200
    return jsonify(response), status_code

@app.route('/authenticate', methods=['POST'])
def authenticate():
    # ToDo - verify input format
    if request.json.get('email') or request.json.get('password') is None:
        # throw error
        status_code = 400
        message = 'Bad request. Did not contain email or password values in JSON'
        response = {'message': message, 'status_code': status_code}
        return response
    else:
        email = request.json.get('email')
        password = request.json.get('password')

        if app.config['DEBUG'] == True:
            message = 'Authorization granted'
            status_code = 200
        else:
            # ToDo check User service to see if matches
            # ToDo - probably should handle pw as hashes
            # ToDo - return JWT token?
            message = 'foo'
            status_code = 200
        response = {'message': message, 'status_code': status_code}
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
        message = 'Bad request. Did not contain email or password values in JSON'
        response = {'message': message, 'status_code': status_code}
        return response
    # ToDo - Try/Except communication with database
    # ToDo - UUID for account ID
    account_info = f"(14, '{name}', '{email}', '{password}', 'Active', False)"
    insert_sql = f'''
    INSERT INTO ACCOUNT_DIM (ACCOUNT_ID, NAME, EMAIL, PASSWORD, ACCOUNT_STATUS, IS_ADMIN)
    VALUES
    {account_info};
    '''
    # ToDo - adjust function to accomodate
    conn = psycopg2.connect(f"dbname='accounts' user='postgres' host='localhost' password='secret_password'")
    cursor = conn.cursor()
    cursor.execute(insert_sql)
    # rows = cursor.fetchall() # cursor.rowcount
    conn.commit()
    conn.close()

    status_code = 200
    response = {'message': 'Account successfully created', 'status_code': status_code}
    return response

@app.route('/deleteAccount', methods=['POST'])
def deleteAccount():
    # ToDo - verify input format 
    account_id = request.json.get('account_id')
    # ToDo - communicate with DB
    status_code = 200
    response = {'message': 'Account successfully deleted', 'status_code': status_code}
    return response

@app.route('/suspendAccount', methods=['POST'])
def suspendAccount():
    # ToDo - verify input format 
    account_id = request.json.get('account_id')
    # ToDo - communicate with DB
    status_code = 200
    response = {'message': 'Account successfully suspended', 'status_code': status_code}
    return response

@app.route('/updateAccount', methods=['POST'])
def updateAccount():
    # ToDo - verify input format 
    account_id = request.json.get('account_id')
    update_params = request.json.get()
    # ToDo - communicate with DB
    status_code = 200
    response = {'message': 'Account successfully updated', 'status_code': status_code}
    return response


# getAccount
# createAccount
# deleteAccount
# updateAccount
# suspendAccount


app.run(host='0.0.0.0', port=5001)