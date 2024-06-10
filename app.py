import os

from flask import Flask, jsonify, request
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL from environment variables
app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "default_user")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "default_password")
app.config["MYSQL_DB"] = os.environ.get("MYSQL_DB", "default_db")

# Initialize MySQL
mysql = MySQL(app)


@app.route("/")
def hello():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM seats")
    results = [
        {"seat_number": seat_number, "on_break": on_break}
        for (seat_number, on_break) in cur
    ]
    cur.close()

    return jsonify({"results": results})


@app.route("/clear", methods=["POST"])
def clear():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM seats")
    mysql.connection.commit()
    cur.close()
    return (
        jsonify({"message": "All seats are now free and removed from the database"}),
        200,
    )


@app.route("/claim", methods=["POST"])
def claim():
    seat_number = request.json.get("seat_number")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM seats WHERE seat_number = %s", (seat_number,))
    if cur.fetchone():
        cur.close()
        return jsonify({"message": "Seat already claimed"}), 400

    cur.execute(
        "INSERT INTO seats (seat_number, on_break) VALUES (%s, %s)",
        (seat_number, False),
    )
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Seat claimed successfully"}), 200


@app.route("/leave", methods=["POST"])
def leave():
    seat_number = request.json.get("seat_number")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM seats WHERE seat_number = %s", (seat_number,))
    if not cur.fetchone():
        cur.close()
        return jsonify({"message": "Seat already free"}), 400

    cur.execute("DELETE FROM seats WHERE seat_number = %s", (seat_number,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Seat left successfully"}), 200


@app.route("/break", methods=["POST"])
def on_break():
    seat_number = request.json.get("seat_number")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM seats WHERE seat_number = %s", (seat_number,))
    if not cur.fetchone():
        cur.close()
        return jsonify({"message": "Seat not found"}), 400

    cur.execute("UPDATE seats SET on_break = 1 WHERE seat_number = %s", (seat_number,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Seat is now on break"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
