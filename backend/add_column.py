import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="multi_industrial_dev",
    user="postgres",
    password="your_password"
)

cursor = conn.cursor()
cursor.execute("ALTER TABLE users ADD COLUMN name VARCHAR(255);")
conn.commit()
cursor.close()
conn.close()

print("Column added!")