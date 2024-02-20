from flask import Flask
import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='416G@*zy8k4r12',
                             database='sakila',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

api = Flask(__name__)

@api.route('/profile')
def get_actors():
    cursor=connection.cursor()
    sql = "SELECT * from actor"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result