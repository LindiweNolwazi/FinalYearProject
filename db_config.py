db_config={
    'host':'localhost',
    'user':'root',
    'password':'Sthelosothando@04',
    'database':'Final_Year_Project'
}

def connect_db():
    import mysql.connector
    return mysql.connector.connect(**db_config)

