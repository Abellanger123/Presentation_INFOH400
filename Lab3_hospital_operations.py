import sqlite3

# Database connection
db_file_path = "hospital.db"
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

### Function to insert a person and avoid duplicates
def insert_person(firstname, familyname, dateofbirth):
    cursor.execute("""
        SELECT idperson FROM Person WHERE firstname = ? AND familyname = ? AND dateofbirth = ?
    """, (firstname, familyname, dateofbirth))
    result = cursor.fetchone()

    if result:
        print(f"Person {firstname} {familyname} already exists.")
        return result[0]

    cursor.execute("""
        INSERT INTO Person (firstname, familyname, dateofbirth)
        VALUES (?, ?, ?)
    """, (firstname, familyname, dateofbirth))
    conn.commit()
    return cursor.lastrowid

### Function to insert a doctor
def insert_doctor(firstname, familyname, dateofbirth, specialty, email, password):
    person_id = insert_person(firstname, familyname, dateofbirth)

    cursor.execute("SELECT email FROM Credentials WHERE email = ?", (email,))
    if cursor.fetchone():
        print(f"Email {email} already exists.")
        return

    cursor.execute("""
        INSERT INTO Doctor (idperson, specialty) 
        VALUES (?, ?)
    """, (person_id, specialty))

    cursor.execute("""
        INSERT INTO Credentials (email, password, designation, person_id, date_of_birth) 
        VALUES (?, ?, 'Doctor', ?, ?)
    """, (email, password, person_id, dateofbirth))

    conn.commit()
    print(f"Doctor {firstname} {familyname} added with email {email}.")

### Function to insert a patient
def insert_patient(firstname, familyname, dateofbirth, phonenumber, email, password):
    person_id = insert_person(firstname, familyname, dateofbirth)

    cursor.execute("SELECT email FROM Credentials WHERE email = ?", (email,))
    if cursor.fetchone():
        print(f"Email {email} already exists.")
        return

    cursor.execute("""
        INSERT INTO Patient (idperson, phonenumber) 
        VALUES (?, ?)
    """, (person_id, phonenumber))

    cursor.execute("""
        INSERT INTO Credentials (email, password, designation, person_id, date_of_birth) 
        VALUES (?, ?, 'Patient', ?, ?)
    """, (email, password, person_id, dateofbirth))

    conn.commit()
    print(f"Patient {firstname} {familyname} added with email {email}.")

### Function to update a person's information
def update_person(person_id, firstname=None, familyname=None, dateofbirth=None):
    update_query = "UPDATE Person SET "
    params = []

    if firstname:
        update_query += "firstname = ?, "
        params.append(firstname)
    if familyname:
        update_query += "familyname = ?, "
        params.append(familyname)
    if dateofbirth:
        update_query += "dateofbirth = ?, "
        params.append(dateofbirth)

    # Remove the trailing comma and add the WHERE clause
    update_query = update_query.rstrip(", ") + " WHERE idperson = ?"
    params.append(person_id)

    cursor.execute(update_query, tuple(params))
    conn.commit()
    print(f"Person with ID {person_id} updated.")

### Function to update a doctor's specialty
def update_doctor(doctor_id, specialty):
    cursor.execute("""
        UPDATE Doctor 
        SET specialty = ? 
        WHERE iddoctor = ?
    """, (specialty, doctor_id))
    conn.commit()
    print(f"Doctor with ID {doctor_id} updated with specialty {specialty}.")

### Function to update a patient's phone number
def update_patient(patient_id, phonenumber):
    cursor.execute("""
        UPDATE Patient 
        SET phonenumber = ? 
        WHERE idpatient = ?
    """, (phonenumber, patient_id))
    conn.commit()
    print(f"Patient with ID {patient_id} updated with phone number {phonenumber}.")

### Function to delete a person
def delete_person(person_id):
    cursor.execute("DELETE FROM Person WHERE idperson = ?", (person_id,))
    conn.commit()
    print(f"Person with ID {person_id} deleted.")

### Function to delete a doctor
def delete_doctor(doctor_id):
    cursor.execute("SELECT idperson FROM Doctor WHERE iddoctor = ?", (doctor_id,))
    person_id = cursor.fetchone()
    if person_id:
        delete_person(person_id[0])

### Function to delete a patient
def delete_patient(patient_id):
    cursor.execute("SELECT idperson FROM Patient WHERE idpatient = ?", (patient_id,))
    person_id = cursor.fetchone()
    if person_id:
        delete_person(person_id[0])

### Example Usage

# Insert sample data
insert_doctor("Alice", "Johnson", "1980-05-20", "Cardiology", "alice.johnson@hospital.com", "password123")
insert_patient("Bob", "Smith", "1990-01-15", 123456789, "bob.smith@hospital.com", "password456")

# Additional Doctor and Patient
insert_doctor("Emily", "Davis", "1987-11-05", "Orthopedics", "emily.davis@hospital.com", "pass789")
insert_patient("Charlie", "Brown", "1992-04-30", 222333444, "charlie.brown@hospital.com", "pass789")

# Update person
update_person(1, firstname="Alicia", familyname="Johns", dateofbirth="1981-01-01")

# Update doctor specialty
update_doctor(1, "Neurology")
update_doctor(2, "Pediatrics")  # Update Emily Davis' specialty

# Update patient phone number
update_patient(2, 987654321)
update_patient(3, 666777888)  # Update Charlie Brown's phone number


# Close connection
cursor.close()
conn.close()
print("Data operations completed.")


