import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename
from threading import Thread
import queue
import sqlite3
import socket
from hl7apy.parser import parse_message, Message

# === Configuration ===
HL7_SEND_PORT = 2575
HL7_RECEIVE_PORT = 2575
DB_PATH = "hospital.db"

# === HL7 Server ===
class HL7Server(Thread):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
        self.running = True

    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(('localhost', HL7_RECEIVE_PORT))
                server_socket.listen(1)
                self.log_queue.put("HL7 Server started and listening...")
                while self.running:
                    conn, addr = server_socket.accept()
                    with conn:
                        data = conn.recv(4096)
                        if data:
                            msg = data.decode(errors='ignore')
                            parsed_msg = parse_message(msg, validation_level=2)
                            self.log_queue.put(f"Received HL7 message:\n{parsed_msg.to_er7()}")
                            self.save_patient_from_message(parsed_msg)
        except Exception as e:
            self.log_queue.put(f"Server error: {e}")

    def stop(self):
        self.running = False
        self.log_queue.put("HL7 Server stopped.")

    def save_patient_from_message(self, parsed_msg):
        try:
            # Safely get PID
            pid = None
            for seg in parsed_msg.children:
                if seg.name == 'PID':
                    pid = seg
                    break

            if not pid:
                self.log_queue.put("No PID segment found in message.")
                return

            name_parts = pid.pid_5.value.split('^')
            familyname = name_parts[0]
            firstname = name_parts[1] if len(name_parts) > 1 else "Unknown"
            dateofbirth = pid.pid_7.value
            phone = pid.pid_13.value if pid.pid_13 else '0000000000'
            dateofbirth_formatted = f"{dateofbirth[:4]}-{dateofbirth[4:6]}-{dateofbirth[6:]}"

            email = f"{firstname.lower()}.{familyname.lower()}@hospital.com"
            default_password = "default123"

            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()

                # Check if person exists
                cur.execute("""
                    SELECT idperson FROM Person 
                    WHERE firstname=? AND familyname=? AND dateofbirth=?
                """, (firstname, familyname, dateofbirth_formatted))
                existing = cur.fetchone()

                if existing:
                    idperson = existing[0]
                    self.log_queue.put(f"Person {firstname} {familyname} already exists.")
                else:
                    cur.execute("""
                        INSERT INTO Person (firstname, familyname, dateofbirth) 
                        VALUES (?, ?, ?)
                    """, (firstname, familyname, dateofbirth_formatted))
                    idperson = cur.lastrowid
                    self.log_queue.put(f"Inserted new person: {firstname} {familyname}.")

                # Check if already a patient
                cur.execute("SELECT * FROM Patient WHERE idperson = ?", (idperson,))
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO Patient (idperson, phonenumber, is_active) 
                        VALUES (?, ?, 1)
                    """, (idperson, phone))
                    self.log_queue.put(f"Patient {firstname} {familyname} added with phone {phone}.")
                else:
                    self.log_queue.put(f"{firstname} {familyname} is already a registered patient.")

                # Check if credentials exist
                cur.execute("SELECT * FROM Credentials WHERE person_id = ?", (idperson,))
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO Credentials (email, password, designation, person_id, date_of_birth)
                        VALUES (?, ?, 'Patient', ?, ?)
                    """, (email, default_password, idperson, dateofbirth_formatted))
                    self.log_queue.put(f"Credentials created: {email} / {default_password}")
                else:
                    self.log_queue.put("Credentials already exist for this person.")

                conn.commit()

        except Exception as e:
            self.log_queue.put(f"Error saving patient from HL7: {e}")




# === HL7 Client ===
class HL7Client:
    def __init__(self, log_queue):
        self.log_queue = log_queue

    def send_message(self, hl7_message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', HL7_SEND_PORT))
                s.sendall(hl7_message.to_er7().encode())
                self.log_queue.put("Message sent successfully")
        except Exception as e:
            self.log_queue.put(f"Error sending message: {e}")


# === Main App GUI ===
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lightweight HL7 Services")
        self.log_queue = queue.Queue()
        self.hl7_server = HL7Server(self.log_queue)
        self.hl7_client = HL7Client(self.log_queue)
        self.create_widgets()
        self.populate_patient_dropdown()
        self.update_logs()

    def create_widgets(self):
        ttk.Label(self, text="Lightweight HL7 Services", font=("Tahoma", 18, "bold")).pack(padx=10, pady=10)

        self.open_message_button = ttk.Button(self, text="Open message", command=self.open_message)
        self.open_message_button.pack(pady=5)

        self.message_explorer = tk.Text(self, height=5, width=70)
        self.message_explorer.pack(pady=5)

        self.start_listener_button = ttk.Button(self, text="Start Listener", command=self.start_listener)
        self.start_listener_button.pack(pady=5)

        self.send_message_button = ttk.Button(self, text="Send", command=self.send_message)
        self.send_message_button.pack(pady=5)

        self.log_display = tk.Text(self, height=10, width=70, state='disabled')
        self.log_display.pack(pady=5)

        self.patient_frame = ttk.Frame(self)
        self.patient_frame.pack(pady=10)

        ttk.Label(self.patient_frame, text="Select patient:").pack(side=tk.LEFT)

        self.patient_var = tk.StringVar()
        self.patient_dropdown = ttk.Combobox(self.patient_frame, textvariable=self.patient_var)
        self.patient_dropdown.pack(side=tk.LEFT)

        self.send_patient_button = ttk.Button(self.patient_frame, text="Send Patient Info", command=self.send_patient_info)
        self.send_patient_button.pack(side=tk.LEFT, padx=5)

    def populate_patient_dropdown(self):
        try:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            cur.execute("""
                SELECT Person.firstname || ' ' || Person.familyname
                FROM Patient
                JOIN Person ON Patient.idperson = Person.idperson
                WHERE Patient.is_active = 1
            """)
            patients = [row[0] for row in cur.fetchall()]
            con.close()
            self.patient_dropdown['values'] = patients
        except Exception as e:
            messagebox.showerror('Error', f'Failed to populate patient list: {e}')

    def open_message(self):
        filename = askopenfilename(filetypes=[("HL7 files", "*.hl7")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.message_explorer.delete('1.0', tk.END)
                self.message_explorer.insert(tk.END, content)
                self.log_queue.put(f"Loaded HL7 message from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def start_listener(self):
        if not self.hl7_server.is_alive():
            self.hl7_server.start()
            self.log_queue.put("Listener started.")
        else:
            self.log_queue.put("Listener already running")

    def send_message(self):
        if self.hl7_server.is_alive():
            try:
                msg = Message("ADT_A01")
                msg.msh.msh_2 = "^~\\&"
                msg.msh.msh_9 = "ADT^A01"
                msg.msh.msh_10 = "123456"
                msg.msh.msh_11 = "P"
                msg.pid.pid_3 = "9999"
                msg.pid.pid_5 = "Johnson^David"
                msg.pid.pid_7 = "19850512"
                msg.pid.pid_13 = "5551234567"
                self.hl7_client.send_message(msg)
                self.log_queue.put("HL7 message sent.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")

    def send_patient_info(self):
        try:
            selected_patient = self.patient_var.get()
            if not selected_patient:
                messagebox.showwarning("Warning", "Please select a patient.")
                return

            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()
            cur.execute("""
                SELECT Patient.idpatient, Person.idperson, Patient.phonenumber, Person.dateofbirth, 
                       Person.firstname, Person.familyname, Patient.is_active
                FROM Patient
                JOIN Person ON Patient.idperson = Person.idperson
                WHERE Person.firstname || ' ' || Person.familyname = ?
            """, (selected_patient,))
            patient = cur.fetchone()

            if patient:
                idpatient, idperson, phonenumber, dob, firstname, familyname, is_active = patient
                msg = Message("ADT_A01")
                msg.msh.msh_2 = "^~\\&"
                msg.msh.msh_9 = "ADT^A01"
                msg.msh.msh_10 = "123456"
                msg.msh.msh_11 = "P"
                msg.pid.pid_3 = str(idpatient)
                msg.pid.pid_5 = f"{familyname}^{firstname}"
                msg.pid.pid_7 = dob.replace("-", "")
                msg.pid.pid_13 = str(phonenumber)

                if messagebox.askyesno("Confirm", f"Send HL7 message for {firstname}?"):
                    self.hl7_client.send_message(msg)
                else:
                    self.log_queue.put("Message cancelled by user.")
            else:
                messagebox.showerror("Error", "Selected patient not found in database.")
            con.close()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def update_logs(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_display.config(state='normal')
            self.log_display.insert(tk.END, message + "\n")
            self.log_display.config(state='disabled')
        self.after(1000, self.update_logs)


# === App Entry Point ===
def main():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()

