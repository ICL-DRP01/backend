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
        {"seat_id": seat_id, "seat_number": seat_number, "is_booked": is_booked}
        for (seat_id, seat_number, is_booked) in cur
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
    data = request.json
    seat_number = data.get("seat_number")
    if seat_number:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM seats WHERE seat_number = %s", [seat_number])
        seat = cur.fetchone()
        if seat:
            if seat[2]:  # if is_booked is True
                return jsonify({"error": "Seat is already claimed"}), 400
            else:
                cur.execute(
                    "UPDATE seats SET is_booked = TRUE WHERE seat_number = %s",
                    [seat_number],
                )
        else:
            cur.execute(
                "INSERT INTO seats (seat_number, is_booked) VALUES (%s, TRUE)",
                [seat_number],
            )
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": f"Seat {seat_number} claimed successfully"}), 200
    return jsonify({"error": "Seat number not provided"}), 400


@app.route("/leave", methods=["POST"])
def leave():
    data = request.json
    seat_number = data.get("seat_number")
    if seat_number:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM seats WHERE seat_number = %s", [seat_number])
        seat = cur.fetchone()
        if seat:
            if not seat[2]:  # if is_booked is False
                return jsonify({"error": "Seat is already free"}), 400
            else:
                cur.execute("DELETE FROM seats WHERE seat_number = %s", [seat_number])
        else:
            return jsonify({"error": "Seat does not exist"}), 400
        mysql.connection.commit()
        cur.close()
        return (
            jsonify(
                {
                    "message": f"Seat {seat_number} is now free and removed from the database"
                }
            ),
            200,
        )
    return jsonify({"error": "Seat number not provided"}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
