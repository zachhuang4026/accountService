import psycopg2

try:
    # Create connection to database 
    conn = psycopg2.connect("dbname='accounts' user='postgres' host='localhost' password='secret_password'")
    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    print('DB CONNECTION ESTABLISHED........')

    # Define Account dim table
    drop_sql = '''
    DROP TABLE IF EXISTS ACCOUNT_DIM;
    '''
    cursor.execute(drop_sql)

    create_sql = '''
    CREATE TABLE IF NOT EXISTS ACCOUNT_DIM(
        ACCOUNT_ID TEXT NOT NULL,
        NAME TEXT NOT NULL,
        EMAIL TEXT NOT NULL,
        PASSWORD TEXT NOT NULL,
        ACCOUNT_STATUS TEXT NOT NULL,
        IS_ADMIN BOOLEAN NOT NULL
    )
    '''
    cursor.execute(create_sql)
    print("ACCOUNT_DIM Table created successfully........")

    # INSERT DEFAULT VALUES
    insert_sql = '''
    INSERT INTO ACCOUNT_DIM (ACCOUNT_ID, NAME, EMAIL, PASSWORD, ACCOUNT_STATUS, IS_ADMIN)
    VALUES
    ('1', 'Admin', 'admin', 'admin', 'Active', True),
    ('2', 'User', 'user', 'user', 'Active', False);
    '''
    cursor.execute(insert_sql)
    print("Default values inserted into ACCOUNT_DIM successfully........")
    
    conn.commit()
    conn.close()
except:
    print("Error creating Account table")

