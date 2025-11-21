import mysql.connector
def get_connect():
    return mysql.connector.connect(
    user="root",
    password="12345678",
    host="localhost",
    database="website"
)
print("connect succeed")
# 建立 cursor 物件
