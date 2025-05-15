from flask import Flask, render_template, request
from scheduler import generate_schedule
from collections import defaultdict

app = Flask(__name__)

def format_schedule_table(schedule):
    table = defaultdict(dict)
    time_slots = sorted(set(row["time"] for row in schedule))
    rooms = sorted(set(row["room"] for row in schedule))

    for entry in schedule:
        value = f"{entry['class']}<br>{entry['subject']}<br>{entry['teacher']}"
        table[entry["time"]][entry["room"]] = value

    return time_slots, rooms, table

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    times, rooms, table = [], [], {}
    if request.method == "POST":
        try:
            num_classes = int(request.form["num_classes"])
            num_teachers = int(request.form["num_teachers"])
            subjects = [s.strip() for s in request.form["subjects"].split(",")]
            num_rooms = int(request.form["num_rooms"])
            result = generate_schedule(num_classes, num_teachers, subjects, num_rooms)
            if "schedule" in result:
                times, rooms, table = format_schedule_table(result["schedule"])
        except Exception as e:
            result = {"error": f"Lỗi: {str(e)}"}
    return render_template("index.html", result=result, times=times, rooms=rooms, table=table)

if __name__ == "__main__":
    app.run(debug=True)