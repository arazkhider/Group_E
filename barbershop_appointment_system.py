from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote
from uuid import uuid4

from flask import Flask, jsonify, redirect, render_template_string, request, send_file, url_for

APP_TITLE = "Araz Salon"
DB_PATH = Path(__file__).with_name("appointments.db")

BARBERS = {
    "Araz": {
        "work_days": {0, 1, 2, 3, 4, 5, 6},  # Monday=0 ... Sunday=6
        "start_hour": 9,
        "end_hour": 17,
    },
    "Hozan": {
        "work_days": {0, 2, 4},  # Monday, Wednesday, Friday
        "start_hour": 9,
        "end_hour": 17,
    },
    "Ahmad": {
        "work_days": {0, 1, 2, 3, 4, 5, 6},
        "start_hour": 9,
        "end_hour": 17,
    },
}

SERVICES = {
    "hair_cut": {"name": "Hair Cutting", "price_eur": 30, "duration_minutes": 45},
    "waxing": {"name": "Waxing", "price_eur": 5, "duration_minutes": 15},
    "beard": {"name": "Beard", "price_eur": 15, "duration_minutes": 30},
    "hair_and_beard": {"name": "Hair + Beard", "price_eur": 40, "duration_minutes": 60},
}


@dataclass
class Appointment:
    id: int
    booking_code: str
    customer_name: str
    customer_phone: str
    barber_name: str
    service_key: str
    start_datetime: datetime
    end_datetime: datetime
    notes: str
    created_at: datetime


app = Flask(__name__)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_conn()) as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_code TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                barber_name TEXT NOT NULL,
                service_key TEXT NOT NULL,
                start_datetime TEXT NOT NULL,
                end_datetime TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )


def barber_is_working(barber_name: str, start_dt: datetime, end_dt: datetime) -> bool:
    barber = BARBERS.get(barber_name)
    if not barber:
        return False

    if start_dt.weekday() not in barber["work_days"]:
        return False

    starts_at = start_dt.replace(hour=barber["start_hour"], minute=0, second=0, microsecond=0)
    ends_at = start_dt.replace(hour=barber["end_hour"], minute=0, second=0, microsecond=0)

    return starts_at <= start_dt and end_dt <= ends_at


def barber_has_conflict(barber_name: str, start_dt: datetime, end_dt: datetime) -> bool:
    with closing(get_conn()) as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM appointments
            WHERE barber_name = ?
              AND (? < end_datetime)
              AND (? > start_datetime)
            LIMIT 1
            """,
            (barber_name, start_dt.isoformat(), end_dt.isoformat()),
        ).fetchone()
    return row is not None


def service_options() -> List[Dict[str, str]]:
    return [
        {
            "key": key,
            "name": value["name"],
            "price": f"{value['price_eur']}€",
            "duration": f"{value['duration_minutes']} min",
        }
        for key, value in SERVICES.items()
    ]


def serialize_appointment(row: sqlite3.Row) -> Dict[str, str]:
    service = SERVICES[row["service_key"]]
    return {
        "id": row["id"],
        "booking_code": row["booking_code"],
        "customer_name": row["customer_name"],
        "customer_phone": row["customer_phone"],
        "barber_name": row["barber_name"],
        "service": service["name"],
        "price_eur": service["price_eur"],
        "start_datetime": row["start_datetime"],
        "end_datetime": row["end_datetime"],
        "notes": row["notes"],
        "created_at": row["created_at"],
    }


@app.get("/")
def home():
    with closing(get_conn()) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM appointments
            ORDER BY start_datetime ASC
            """
        ).fetchall()

    appointments = [serialize_appointment(row) for row in rows]
    return render_template_string(
        """
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{{ title }} - Booking</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 980px; margin: 1.5rem auto; line-height: 1.3; }
                h1, h2 { margin-bottom: .4rem; }
                table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
                th, td { border: 1px solid #ddd; padding: .5rem; text-align: left; }
                th { background: #f2f2f2; }
                form { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin-top: 1rem; }
                form label { display: block; font-weight: bold; }
                form input, form select, form textarea { width: 100%; padding: .4rem; margin-top: .2rem; }
                .full { grid-column: 1 / -1; }
                button { padding: .6rem 1rem; border: none; background: #222; color: white; cursor: pointer; }
                .small { font-size: .9rem; color: #555; }
            </style>
        </head>
        <body>
            <h1>{{ title }} Appointment System</h1>
            <p>Book appointments by barber, show prices, and export each booking to a mobile calendar.</p>

            <h2>Service Prices</h2>
            <table>
                <tr><th>Service</th><th>Price</th><th>Duration</th></tr>
                {% for item in services %}
                <tr><td>{{ item.name }}</td><td>{{ item.price }}</td><td>{{ item.duration }}</td></tr>
                {% endfor %}
            </table>

            <h2>Book Appointment</h2>
            <form method="post" action="{{ url_for('create_appointment') }}">
                <div><label>Customer Name<input name="customer_name" required></label></div>
                <div><label>Phone Number<input name="customer_phone" required></label></div>
                <div>
                    <label>Barber
                        <select name="barber_name" required>
                            {% for barber in barbers %}<option value="{{ barber }}">{{ barber }}</option>{% endfor %}
                        </select>
                    </label>
                </div>
                <div>
                    <label>Service
                        <select name="service_key" required>
                            {% for item in services %}<option value="{{ item.key }}">{{ item.name }} ({{ item.price }})</option>{% endfor %}
                        </select>
                    </label>
                </div>
                <div><label>Date<input name="date" type="date" required></label></div>
                <div><label>Time<input name="time" type="time" min="09:00" max="16:30" required></label></div>
                <div class="full"><label>Notes<textarea name="notes"></textarea></label></div>
                <div class="full"><button type="submit">Create Appointment</button></div>
            </form>

            <h2>All Appointments</h2>
            <table>
                <tr>
                    <th>Booking Code</th><th>Customer</th><th>Phone</th><th>Barber</th><th>Service</th><th>Start</th><th>Calendar</th>
                </tr>
                {% for item in appointments %}
                <tr>
                    <td>{{ item.booking_code }}</td>
                    <td>{{ item.customer_name }}</td>
                    <td>{{ item.customer_phone }}</td>
                    <td>{{ item.barber_name }}</td>
                    <td>{{ item.service }} ({{ item.price_eur }}€)</td>
                    <td>{{ item.start_datetime }}</td>
                    <td>
                      <a href="{{ url_for('download_ics', booking_code=item.booking_code) }}">.ics</a> |
                      <a href="{{ url_for('google_calendar_link', booking_code=item.booking_code) }}">Google</a>
                    </td>
                </tr>
                {% endfor %}
            </table>
            <p class="small">Hozan works Monday/Wednesday/Friday from 09:00 to 17:00. Araz and Ahmad work daily from 09:00 to 17:00.</p>
        </body>
        </html>
        """,
        title=APP_TITLE,
        services=service_options(),
        barbers=list(BARBERS.keys()),
        appointments=appointments,
    )


@app.post("/appointments")
def create_appointment():
    customer_name = request.form.get("customer_name", "").strip()
    customer_phone = request.form.get("customer_phone", "").strip()
    barber_name = request.form.get("barber_name", "").strip()
    service_key = request.form.get("service_key", "").strip()
    date_part = request.form.get("date", "").strip()
    time_part = request.form.get("time", "").strip()
    notes = request.form.get("notes", "").strip()

    if not all([customer_name, customer_phone, barber_name, service_key, date_part, time_part]):
        return jsonify({"error": "All required fields must be filled."}), 400

    if service_key not in SERVICES:
        return jsonify({"error": "Invalid service selected."}), 400

    try:
        start_dt = datetime.fromisoformat(f"{date_part}T{time_part}")
    except ValueError:
        return jsonify({"error": "Invalid date or time format."}), 400

    duration = SERVICES[service_key]["duration_minutes"]
    end_dt = start_dt + timedelta(minutes=duration)

    if not barber_is_working(barber_name, start_dt, end_dt):
        return jsonify({"error": "Barber is not available at this date/time."}), 400

    if barber_has_conflict(barber_name, start_dt, end_dt):
        return jsonify({"error": "The barber already has an appointment in this time slot."}), 409

    booking_code = f"AZ-{uuid4().hex[:8].upper()}"

    with closing(get_conn()) as conn, conn:
        conn.execute(
            """
            INSERT INTO appointments (
                booking_code, customer_name, customer_phone, barber_name,
                service_key, start_datetime, end_datetime, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                booking_code,
                customer_name,
                customer_phone,
                barber_name,
                service_key,
                start_dt.isoformat(),
                end_dt.isoformat(),
                notes,
                datetime.utcnow().isoformat(),
            ),
        )

    return redirect(url_for("home"))


@app.get("/api/appointments")
def api_appointments():
    with closing(get_conn()) as conn:
        rows = conn.execute("SELECT * FROM appointments ORDER BY start_datetime ASC").fetchall()
    return jsonify([serialize_appointment(row) for row in rows])


@app.get("/appointments/<booking_code>/ics")
def download_ics(booking_code: str):
    with closing(get_conn()) as conn:
        row = conn.execute("SELECT * FROM appointments WHERE booking_code = ?", (booking_code,)).fetchone()

    if not row:
        return jsonify({"error": "Booking code not found."}), 404

    appointment = serialize_appointment(row)
    ics_text = build_ics(appointment)
    file_path = Path(__file__).with_name(f"{booking_code}.ics")
    file_path.write_text(ics_text, encoding="utf-8")

    return send_file(file_path, as_attachment=True, download_name=f"{booking_code}.ics")


@app.get("/appointments/<booking_code>/google")
def google_calendar_link(booking_code: str):
    with closing(get_conn()) as conn:
        row = conn.execute("SELECT * FROM appointments WHERE booking_code = ?", (booking_code,)).fetchone()

    if not row:
        return jsonify({"error": "Booking code not found."}), 404

    appointment = serialize_appointment(row)
    start = datetime.fromisoformat(appointment["start_datetime"]).strftime("%Y%m%dT%H%M%S")
    end = datetime.fromisoformat(appointment["end_datetime"]).strftime("%Y%m%dT%H%M%S")

    title = quote(f"{APP_TITLE} - {appointment['service']} with {appointment['barber_name']}")
    details = quote(
        f"Booking Code: {appointment['booking_code']}\\n"
        f"Customer: {appointment['customer_name']}\\n"
        f"Phone: {appointment['customer_phone']}"
    )

    link = (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={title}"
        f"&dates={start}/{end}"
        f"&details={details}"
    )
    return redirect(link)


def build_ics(appointment: Dict[str, str]) -> str:
    start = datetime.fromisoformat(appointment["start_datetime"]).strftime("%Y%m%dT%H%M%S")
    end = datetime.fromisoformat(appointment["end_datetime"]).strftime("%Y%m%dT%H%M%S")
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    return "\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//ArazSalon//Appointments//EN",
            "BEGIN:VEVENT",
            f"UID:{appointment['booking_code']}@arazsalon",
            f"DTSTAMP:{now}",
            f"DTSTART:{start}",
            f"DTEND:{end}",
            f"SUMMARY:{APP_TITLE} - {appointment['service']} ({appointment['barber_name']})",
            f"DESCRIPTION:Booking code {appointment['booking_code']} - {appointment['customer_name']} ({appointment['customer_phone']})",
            "END:VEVENT",
            "END:VCALENDAR",
            "",
        ]
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
