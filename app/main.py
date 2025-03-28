import psycopg2
import redis
from flask import Flask, render_template
import os

def get_db_connection():
    conn = psycopg2.connect(
        host="db",    #название из docker-compose
        database="dbtest",
        user="user",
        password="password"
    )
    return conn

# conn = get_db_connection()
conn = psycopg2.connect('postgresql://user:password@127.0.0.1:5432/dbtest')


cursor = conn.cursor()

SQL = "CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY,name VARCHAR(50) NOT NULL);"
cursor.execute(SQL)

SQL = "INSERT INTO test_table (name) VALUES ('Andrew Tom'), ('John Smith');"
cursor.execute(SQL)
conn.commit()
cursor.close()


cache = redis.StrictRedis(host='127.0.0.1', port=6379)


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('main.html')
@app.route('/users/')
def users():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_table")
    all_users = cursor.fetchall()
    cursor.close()
    return render_template('users.html', users=all_users)

@app.route('/users/<int:user_id>/')
def user_profile(user_id):

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_table WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    cache.incr(f'user:{user_id}:visits')
    visits = cache.get(f'user:{user_id}:visits').decode('ascii')

    return render_template('user_profile.html', user=user, visits=visits)


app.run(debug=True, port=5000, host='127.0.0.1')