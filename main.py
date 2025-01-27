import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
from sklearn.linear_model import LinearRegression
import numpy as np
import json

# MongoDB Connection
client = MongoClient("Connection string")
db = client["Project01"]
collection = db["P1Student"]

class Student:
    def _init_(self):
        self.fname = ''
        self.lname = ''
        self.roll_no = 0
        self.cgpa = 0.0
        self.attendance = 0.0
        self.course_id = [0] * 5

# Global variables for input fields
global fname_entry, lname_entry, roll_no_entry, cgpa_entry, course_entry, attendance_entry
global fname_entry1, roll_no_entry1, result_label

def add_student():
    student = {
        "fname": fname_entry.get(),
        "lname": lname_entry.get(),
        "roll_no": int(roll_no_entry.get()),
        "cgpa": float(cgpa_entry.get()),
        "course_id": course_entry.get().split()[:3],
        "attendance": float(attendance_entry.get())
    }
    collection.insert_one(student)
    clear_entries()

def delete_student_fname():
    fname = fname_entry1.get()
    result = collection.delete_many({"fname": fname})
    if result.deleted_count == 0:
        messagebox.showerror("Error", "No such first name found")
    else:
        display_students()

def delete_student_roll():
    roll = int(roll_no_entry1.get())
    result = collection.delete_many({"roll_no": roll})
    if result.deleted_count == 0:
        messagebox.showerror("Error", "No such roll number found")
    else:
        display_students()

def find_student_fname():
    fname = fname_entry1.get()
    found_students = list(collection.find({"fname": fname}))
    if not found_students:
        messagebox.showerror("Error", "No such first name found")
    else:
        display_students(found_students)

def find_student_roll():
    roll = int(roll_no_entry1.get())
    found_students = list(collection.find({"roll_no": roll}))
    if not found_students:
        messagebox.showerror("Error", "No such roll number found")
    else:
        display_students(found_students)

def update_student():
    roll = int(roll_no_entry1.get())
    student = {
        "fname": fname_entry.get(),
        "lname": lname_entry.get(),
        "cgpa": float(cgpa_entry.get()),
        "course_id": course_entry.get().split()[:5],
        "attendance": float(attendance_entry.get())
    }
    result = collection.update_one({"roll_no": roll}, {"$set": student})
    if result.matched_count == 0:
        messagebox.showerror("Error", "No such roll number found")
    else:
        display_students([student])

def short_attendance():
    short_attendance_students = list(collection.find({"attendance": {"$lt": 75}}))
    if short_attendance_students:
        display_students(short_attendance_students)
    else:
        result_label.config(text="None of the students have attendance < 75%")

def total_pass_fail():
    failed_students = list(collection.find({"cgpa": {"$lt": 4.0}}))
    if failed_students:
        display_students(failed_students)
    else:
        result_label.config(text="None of the students have failed")

def avg_cgpa():
    cgpa_list = [student["cgpa"] for student in collection.find({}, {"_id": 0, "cgpa": 1})]
    avg_cgpa = sum(cgpa_list) / len(cgpa_list) if cgpa_list else 0
    result_label.config(text=f"The average CGPA of the class is {avg_cgpa:.2f}")

def finalize_file():
    data = list(collection.find({}, {"_id": 0}))
    with open("student_data.json", "w") as f:
        json.dump(data, f)
    messagebox.showinfo("Success", "Data exported to student_data.json")

def train_model():
    data = list(collection.find({}, {"_id": 0, "attendance": 1, "cgpa": 1}))
    X = np.array([d["attendance"] for d in data]).reshape(-1, 1)
    y = np.array([d["cgpa"] for d in data])
    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_cgpa_button():
    attendance = float(attendance_entry.get())
    model = train_model()
    predicted_cgpa = model.predict(np.array([[attendance]]))[0]
    result_label.config(text=f"Predicted CGPA: {predicted_cgpa:.2f}")

def clear_entries():
    fname_entry.delete(0, tk.END)
    lname_entry.delete(0, tk.END)
    roll_no_entry.delete(0, tk.END)
    cgpa_entry.delete(0, tk.END)
    course_entry.delete(0, tk.END)
    attendance_entry.delete(0, tk.END)

def clear_row():
    for widget in window.grid_slaves():
        if int(widget.grid_info()["row"]) == 9:
            widget.grid_forget()

def display_students(student_list=None):
    student_list = student_list or list(collection.find({}, {"_id": 0}))
    output_text = ""
    if not student_list:
        output_text = "No students match the criteria."
    else:
        for student in student_list:
            output_text += f"Roll Number: {student['roll_no']}\t"
            output_text += f"First Name: {student['fname']}\t"
            output_text += f"Last Name: {student['lname']}\t"
            output_text += f"CGPA: {student['cgpa']}\t"
            output_text += f"Attendance: {student['attendance']}\t"
            output_text += f"Courses: {student['course_id']}\t"
            output_text += "\n\n"
    result_label.config(text=output_text)

# Tkinter GUI Setup
window = tk.Tk()
window.title("Student Database")
window.geometry("1400x730+40+30")
window.resizable(False, False)

background_frame = tk.Frame(window, bg="beige", width=1400, height=730)
background_frame.pack(fill=tk.BOTH, expand=True)
background_frame.pack_propagate(False)

frame_left = tk.Frame(window, bg="beige", width=800, height=500)
frame_left.place(x=0, y=80)
frame_left.pack_propagate(False)

frame_right = tk.Frame(window, bg="pink", width=600, height=650)
frame_right.place(x=830, y=80)
frame_right.pack_propagate(False)

frame_bottom = tk.Frame(window, bg="lightblue", width=800, height=150)
frame_bottom.place(x=0, y=580)

tk.Label(background_frame, text="STUDENT MANAGEMENT", fg="black", bg="beige", font=("Abadi", 23, "bold")).place(x=540, y=5)

# Input Fields
tk.Label(frame_left, text="First Name of Student:", fg="black", bg="white", font=("Microsoft YaHei UI", 11, "bold")).grid(row=0, column=0, padx=10, pady=10)
fname_entry = tk.Entry(frame_left, fg="blue", bg="white", font=("Microsoft YaHei UI", 11), bd=2, relief=tk.SOLID)
fname_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame_left, text="Last Name of Student:", fg="black", bg="white", font=("Microsoft YaHei UI", 11, "bold")).grid(row=1, column=0, padx=10, pady=10)
lname_entry = tk.Entry(frame_left, fg="blue", bg="white", font=("Microsoft YaHei UI", 11), bd=2, relief=tk.SOLID)
lname_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(frame_left, text="Roll Number of Student:", fg="black", bg="white", font=("Microsoft YaHei UI", 11, "bold")).grid(row=2, column=0, padx=10, pady=10)
roll_no_entry = tk.Entry(frame_left, fg="blue", bg="white", font=("Microsoft YaHei UI", 11), bd=2, relief=tk.SOLID)
roll_no_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Label(frame_left, text="CGPA of the Student:", fg="black", bg="white", font=("Microsoft YaHei UI", 11, "bold")).grid(row=3, column=0, padx=10, pady=10)
cgpa_entry = tk.Entry(frame_left, fg="blue", bg="white", font=("Microsoft YaHei UI", 11), bd=2, relief=tk.SOLID)
cgpa_entry.grid(row=3, column=1, padx=10, pady=10)

tk.Label(frame_left, text="Subjects Enrolled (Max:3):", fg="black", bg="white", font=("Microsoft YaHei UI", 11, "bold")).grid(row=4, column=0, padx=10, pady=10)
course_entry = tk.Entry(frame_left, fg="blue", bg="white", font=("Microsoft YaHei UI", 11), bd=2, relief=tk.SOLID)
course_entry.grid(row=4, column=1, padx=10, pady=10)

tk.Label(frame_left, text="Attendance:", fg="black", bg="white", font=("Microsoft YaHei UI", 11, "bold")).grid(row=5, column=0, padx=10, pady=10)
attendance_entry = tk.Entry(frame_left, font=("Microsoft YaHei UI", 11), bg="white", fg="blue", bd=2, relief=tk.SOLID)
attendance_entry.grid(row=5, column=1, padx=10, pady=10)

add_button = tk.Button(frame_left, text="Add Student", font=("Microsoft YaHei UI", 11, "bold"), command=add_student, width=10, border=2, bg="red", fg="white", cursor="hand2")
add_button.grid(row=6, column=1, padx=10, pady=10)

# Operations Menu
menubutton = tk.Menubutton(frame_left, text="Operations Menu", relief=tk.RAISED, borderwidth=2)
menubutton.grid(row=12, column=1, padx=10, pady=10)

menu = tk.Menu(menubutton, tearoff=0)
menu.add_command(label="Delete Student by First Name", command=delete_student_fname)
menu.add_command(label="Delete Student by Roll Number", command=delete_student_roll)
menu.add_command(label="Find Student by First Name", command=find_student_fname)
menu.add_command(label="Find Student by Roll Number", command=find_student_roll)
menu.add_command(label="Update Student", command=update_student)
menu.add_command(label="Short Attendance Students", command=short_attendance)
menu.add_command(label="Total Students Failed", command=total_pass_fail)
menu.add_command(label="Average CGPA", command=avg_cgpa)
menu.add_command(label="Finalize Database", command=finalize_file)
menu.add_command(label="Predict CGPA", command=predict_cgpa_button)
menubutton.configure(menu=menu)
menubutton.configure(bg="beige", fg="black", font=("Microsoft YaHei UI", 11, "bold"), activebackground="powderblue", activeforeground="black", cursor="hand2")

# Output Label
result_label = tk.Label(frame_bottom, text="", fg="brown", bg="lavender", font=("Microsoft YaHei UI", 9, "bold"))
result_label.grid(row=2, columnspan=3)

# Additional Input Fields for Operations
tk.Label(frame_left, text="Enter First Name of Student:", fg="black", bg="white", font=("Microsoft YaHei UI", 11, "bold")).grid(row=9, column=0, padx=10, pady=10)
fname_entry1 = tk.Entry(frame_left, fg="blue", bg="white", font=("Microsoft YaHei UI", 11), bd=2, relief=tk.SOLID)
fname_entry1.grid(row=9, column=1, padx=10, pady=10)

tk.Label(frame_left, text="Enter Roll Number of Student:", fg="black", bg="white", font=("Microsoft YaHei UI", 11, "bold")).grid(row=10, column=0, padx=10, pady=10)
roll_no_entry1 = tk.Entry(frame_left, fg="blue", bg="white", font=("Microsoft YaHei UI", 11), bd=2, relief=tk.SOLID)
roll_no_entry1.grid(row=10, column=1, padx=10, pady=10)

window.mainloop()