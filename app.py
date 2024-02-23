import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='416G@*zy8k4r12',
                             database='sakila',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

with connection:
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * from actor"
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)