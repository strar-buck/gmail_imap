import MySQLdb

def get_database_connection():
    conn = MySQLdb.connect(host="localhost",user="admin",passwd="ritu",db="tenmiles")
    return conn
