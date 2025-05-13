from flask import Flask, render_template, request
from scheduler import generate_schedule

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        try:
            num_classes = int(request.form["num_classes"])
            num_teachers = int(request.form["num_teachers"])
            subjects = [s.strip() for s in request.form["subjects"].split(",")]
            num_rooms = int(request.form["num_rooms"])
            result = generate_schedule(num_classes, num_teachers, subjects, num_rooms)
        except Exception as e:
            result = {"error": f"Lỗi: {str(e)}"}
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)