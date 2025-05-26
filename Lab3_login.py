import sqlite3
import tkinter as tk
from tkinter import messagebox
import re
import subprocess
import os

# Database connection
conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()

# Define HL7 Ports
HL7_SEND_PORT = "2575"
HL7_RECEIVE_PORT = "2575"

# Function to validate email format
def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email)

# Function to handle login
def login():
    email = email_entry.get()
    password = password_entry.get()

    if not email or not password:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    if not is_valid_email(email):
        messagebox.showerror("Error", "Invalid email format!")
        return

    cursor.execute("SELECT * FROM Credentials WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()

    if user:
        user_type = user[3]
        messagebox.showinfo("Success", f"Welcome, {user_type}!")

        if user_type == "Admin":
            open_admin_dashboard()
        elif user_type == "Doctor":
            open_doctor_dashboard(email)
        elif user_type == "Patient":
            open_patient_dashboard()
    else:
        messagebox.showerror("Error", "Invalid email or password!")

def open_admin_dashboard():
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Dashboard")
    tk.Label(admin_window, text="Welcome Admin!", font=("Arial", 14)).pack(pady=20)

def open_doctor_dashboard(email):
    doctor_window = tk.Toplevel(root)
    doctor_window.title("Doctor Dashboard")
    tk.Label(doctor_window, text=f"Welcome Doctor {email}!", font=("Arial", 14)).pack(pady=10)

    # View Patient Information
    view_patient_button = tk.Button(doctor_window, text="View Patient Information", command=view_patient_info)
    view_patient_button.pack(pady=5)

    # Review Past Appointments and Diagnoses
    review_appointments_button = tk.Button(doctor_window, text="Review Appointments/Diagnoses", command=review_appointments)
    review_appointments_button.pack(pady=5)

    # Schedule Appointments
    schedule_appointment_button = tk.Button(doctor_window, text="Schedule Appointment", command=schedule_appointment)
    schedule_appointment_button.pack(pady=5)

    # Record Medical Notes
    record_notes_button = tk.Button(doctor_window, text="Record Medical Notes", command=record_notes)
    record_notes_button.pack(pady=5)

    # Open DICOM Viewer
    open_dicom_button = tk.Button(doctor_window, text="View DICOM Images", command=lambda: open_dicom_viewer(email))
    open_dicom_button.pack(pady=5)

    # Send/Receive Notifications
    notifications_button = tk.Button(doctor_window, text="Send/Receive Notifications", command=send_notifications)
    notifications_button.pack(pady=5)

    # Send Prescription
    send_prescription_button = tk.Button(doctor_window, text="Send Prescription", command=send_prescription)
    send_prescription_button.pack(pady=5)

    # Start HL7 Server
    start_hl7_server_button = tk.Button(doctor_window, text="Start HL7 Server", command=start_hl7_server)
    start_hl7_server_button.pack(pady=5)

    # Send HL7 Message
    send_hl7_button = tk.Button(doctor_window, text="Send HL7 Message", command=send_hl7_message)
    send_hl7_button.pack(pady=5)

def open_patient_dashboard():
    patient_window = tk.Toplevel(root)
    patient_window.title("Patient Dashboard")
    tk.Label(patient_window, text="Welcome Patient!", font=("Arial", 14)).pack(pady=20)

def open_dicom_viewer(email):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dicom_viewer_path = os.path.join(current_dir, "Lab4_5_6_dicom_viewver.py")
        subprocess.Popen(["python", dicom_viewer_path, email])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open DICOM Viewer: {e}")

def start_hl7_server():
    """
    Start the HL7 server to receive messages.
    """
    hl7rcv_path = os.path.join(os.path.dirname(__file__), "dcm4che-5.25.1", "bin", "hl7rcv.bat")
    
    if not os.path.exists(hl7rcv_path):
        messagebox.showerror("Error", f"{hl7rcv_path} not found!")
        return

    try:
        # Crée un répertoire pour stocker les messages HL7 reçus
        hl7_storage_dir = "received_hl7"
        os.makedirs(hl7_storage_dir, exist_ok=True)
        
        # Lancer le serveur HL7
        subprocess.Popen([hl7rcv_path, "-b", "localhost:2580", "--directory", hl7_storage_dir])
        messagebox.showinfo("Info", "HL7 server started and listening on port 2580")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start HL7 server: {e}")

def send_hl7_message():
    """
    Send a HL7 message to the HL7 server.
    """
    hl7snd_path = os.path.join(os.path.dirname(__file__), "dcm4che-5.25.1", "bin", "hl7snd.bat")
    
    if not os.path.exists(hl7snd_path):
        messagebox.showerror("Error", f"{hl7snd_path} not found!")
        return

    # Exemples de messages HL7
    hl7_message = """MSH|^~\\&|HIS|Hospital|LAB|LabDept|202305151200||ADT^A01|123456|P|2.4
PID|1|12345|98765||Doe^John||19700101|M"""

    try:
        # Créer un fichier temporaire pour stocker le message HL7
        with open("hl7_message.txt", "w") as file:
            file.write(hl7_message)

        # Envoyer le message HL7
        subprocess.run([hl7snd_path, "-c", "localhost:2580", "hl7_message.txt"])
        messagebox.showinfo("Info", "HL7 message sent successfully")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send HL7 message: {e}")

def view_patient_info():
    messagebox.showinfo("View Patient Information", "Feature under development.")

def review_appointments():
    messagebox.showinfo("Review Appointments", "Feature under development.")

def schedule_appointment():
    messagebox.showinfo("Schedule Appointment", "Feature under development.")

def record_notes():
    messagebox.showinfo("Record Medical Notes", "Feature under development.")

def send_notifications():
    messagebox.showinfo("Notifications", "Feature under development.")

def send_prescription():
    messagebox.showinfo("Send Prescription", "Feature under development.")

# GUI Setup
root = tk.Tk()
root.title("Login Portal")
root.geometry("400x300")

tk.Label(root, text="Enter login credentials", font=("Arial", 14, "bold")).pack(pady=10)
tk.Label(root, text="Email:").pack()
email_entry = tk.Entry(root)
email_entry.pack()

tk.Label(root, text="Password:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

login_button = tk.Button(root, text="Login", command=login)
login_button.pack(pady=10)

root.mainloop()
conn.close()

