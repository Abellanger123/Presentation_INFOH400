import sqlite3

# Database connection
db_file_path = "hospital.db"
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Create tables
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Person (
        idperson INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT NOT NULL,
        familyname TEXT NOT NULL,
        dateofbirth DATE NOT NULL,
        UNIQUE(firstname, familyname, dateofbirth)
    );

    CREATE TABLE IF NOT EXISTS Doctor (
        iddoctor INTEGER PRIMARY KEY AUTOINCREMENT,
        idperson INTEGER NOT NULL,
        specialty TEXT NOT NULL,
        FOREIGN KEY (idperson) REFERENCES Person(idperson) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Patient (
        idpatient INTEGER PRIMARY KEY AUTOINCREMENT,
        idperson INTEGER NOT NULL,
        phonenumber INTEGER NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (idperson) REFERENCES Person(idperson) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        designation TEXT NOT NULL CHECK (designation IN ('Admin', 'Doctor', 'Patient')),
        person_id INTEGER,
        date_of_birth DATE,
        FOREIGN KEY (person_id) REFERENCES Person(idperson) ON DELETE CASCADE
    );
""")

conn.commit()
print("Database and tables created successfully.")

# Close connection
cursor.close()
conn.close()