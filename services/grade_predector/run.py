from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

model = joblib.load("models/logreg_pipeline_model.pkl")

decoded_grade = {
    0: "A",
    1: "A-",
    2: "B",
    3: "B+",
    4: "B-",
    5: "C",
    6: "C+",
    7: "C-",
    8: "F",
}


@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None

    if request.method == "POST":
        new_student_dict = {
            "Instructor_name": request.form["Instructor_name"],
            "Course_id": request.form["Course_id"],
            "Semester": request.form["Semester"],
            "CourseWork": float(request.form["CourseWork"]),
            "Feedback": float(request.form["Feedback"]),
            "Major": request.form["Major"],
            "GPA_Current": float(request.form["GPA_Current"]),
            "GPA_Previous": float(request.form["GPA_Previous"]),
            "Failed_Courses_Count": float(request.form["Failed_Courses_Count"]),
            "Attendance_Rate": float(request.form["Attendance_Rate"]),
            "Quiz_Average": float(request.form["Quiz_Average"]),
            "Project_Score": float(request.form["Project_Score"]),
            "Study_Hours_Per_Week": float(request.form["Study_Hours_Per_Week"]),
            "Preferred_Learning_Mode": request.form["Preferred_Learning_Mode"],
            "Difficulty_Level": request.form["Difficulty_Level"],
            "Required_GPA": float(request.form["Required_GPA"]),
            "Credit_Hours": float(request.form["Credit_Hours"]),
            "Course_Type": request.form["Course_Type"],
            "Year": request.form["Year"],
            "Satisfaction_Level": float(request.form["Satisfaction_Level"]),
        }

        input_df = pd.DataFrame([new_student_dict])
        y_pred = model.predict(input_df)
        prediction = decoded_grade[y_pred[0]]

    return render_template("index.html", prediction=prediction)


if __name__ == "__main__":
    app.run(debug=True)
