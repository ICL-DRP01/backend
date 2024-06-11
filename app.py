#!/usr/bin/env python

import asyncio
import signal
import os

import websockets
import mysql.connector

booked_seats = set()
flagged_seats = set()
break_seats = set()

users = set()

def get_seats(seats: set) -> str:
    return "{}" if not seats else str(seats)

# dataBase = mysql.connector.connect(
#   host = os.environ.get("MYSQL_HOST", "localhost"),
#   user = os.environ.get("MYSQL_USER", "admin"),
#   passwd = os.environ.get("MYSQL_PASSWORD", "admin"),
#   db = os.environ.get("MYSQL_DB", "myDb")
# )


async def update(websocket):
    global booked_seats, flagged_seats, break_seats, users
    try:
        users.add(websocket)
        await websocket.send(
            f"booked: {get_seats(booked_seats)}, flagged: {get_seats(flagged_seats)}, break: {get_seats(break_seats)}"
        )
        # cur = dataBase.cursor()
        async for message in websocket:
            match message.split(" ")[0]:
                case "book":
                    seat = int(message.split(" ")[1])
                    # If seat already booked, send error message to client
                    if seat in booked_seats:
                        await websocket.send("error: seat already booked")
                        continue
                    else:
                        booked_seats.add(seat)
                case "unbook":
                    seat = int(message.split(" ")[1])
                    booked_seats.remove(seat)
                case "flag":
                    seat = int(message.split(" ")[1])
                    flagged_seats.add(seat)
                case "unflag":
                    seat = int(message.split(" ")[1])
                    flagged_seats.remove(seat)
                case "break":
                    seat = int(message.split(" ")[1])
                    break_seats.add(seat)
                case "unbreak":
                    seat = int(message.split(" ")[1])
                    break_seats.remove(seat)
                case "clear":
                    booked_seats = set()
                    flagged_seats = set()
                    break_seats = set()
                    # cur.execute("DELETE FROM seats")
            websockets.broadcast(
                users,
                f"booked: {get_seats(booked_seats)}, flagged: {get_seats(flagged_seats)}, break: {get_seats(break_seats)}",
            )
        # cur.close()
    finally:
        users.remove(websocket)


async def main():
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with websockets.serve(
        update,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
    ):
        await stop


if __name__ == "__main__":
    asyncio.run(main())
