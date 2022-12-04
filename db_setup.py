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
    ('56786785-6a10-4921-bc74-5573af7c7890', 'Admin', 'admin', 'admin', 'Active', True),
    ('34563456-6a10-4921-bc74-5573af707890', 'User', 'user', 'user', 'Active', False),
    ('12341234-6a10-4921-bc74-5573af7ababa', 'Seller', 'seller', 'seller', 'Active', False),
    ('00000000-6a10-4921-bc74-5573af7c7890', 'Buyer', 'buyer', 'buyer', 'Active', False),
    ('10101010-6a10-4921-bc74-5573af7c7890', 'Adam', 'adamlim@uchicago.edu', 'adam', 'Active', True);
    '''
    cursor.execute(insert_sql)
    print("Default values inserted into ACCOUNT_DIM successfully........")
    
    conn.commit()
    conn.close()
except:
    print("Error creating Account table")

