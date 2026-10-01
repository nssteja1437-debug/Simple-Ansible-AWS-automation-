import os

import psycopg
from flask import Flask

app = Flask(__name__)


def get_db_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=os.environ.get("DB_PORT", "5432"),
    )


@app.route("/")
def home():
    return """
    <h1>Python AWS Automation Project</h1>
    <p>Application Status: Running</p>
    <p>Server: AWS EC2</p>
    <p>Deployment: Ansible</p>
    """


@app.route("/health")
def health():
    return {
        "status": "healthy"
    }


@app.route("/users")
def users():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, email, age FROM users ORDER BY id"
            )
            rows = cursor.fetchall()

    return {
        "users": [
            {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "age": row[3],
            }
            for row in rows
        ]
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)