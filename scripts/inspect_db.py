import sqlite3
conn = sqlite3.connect('students.db')
cur = conn.cursor()
for row in cur.execute('select id,name,email,age,career,semester,created_at from students'):
    print(row)
conn.close()
