import psycopg2
con = psycopg2.connect(database="postgres", user="postgres", password="1234abcd", host="127.0.0.1", port="5432")
cur = con.cursor()
cur.execute('SELECT * FROM vlslp order by random() limit 7')
meal = cur.fetchone()
print(meal[1])
