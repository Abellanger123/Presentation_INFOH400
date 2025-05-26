CREATE TABLE IF NOT EXISTS `Person` (
	`idperson` integer primary key NOT NULL UNIQUE,
	`idpatient` INTEGER NOT NULL,
	`iddoctor` INTEGER NOT NULL,
	`firstname` TEXT NOT NULL,
	`familyname` TEXT NOT NULL,
	`dateofbirth` REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS `Doctor` (
	`iddoctor` integer primary key NOT NULL UNIQUE,
	`idperson` INTEGER NOT NULL,
	`specialty` TEXT NOT NULL,
FOREIGN KEY(`idperson`) REFERENCES `Person`(`idperson`)
);
CREATE TABLE IF NOT EXISTS `Patient` (
	`idpatient` integer primary key NOT NULL UNIQUE,
	`idperson` INTEGER NOT NULL,
	`phonenumber` INTEGER NOT NULL,
	`is_active` REAL NOT NULL,
FOREIGN KEY(`idperson`) REFERENCES `Person`(`idperson`)
);
CREATE TABLE IF NOT EXISTS `Appointment` (
	`id_appointment` integer primary key NOT NULL UNIQUE,
	`idpatient` INTEGER NOT NULL,
	`iddoctor` INTEGER NOT NULL,
	`appointment_date` REAL NOT NULL,
	`appointment_time` TEXT NOT NULL,
	`reason` TEXT NOT NULL,
	`price` REAL NOT NULL,
FOREIGN KEY(`idpatient`) REFERENCES `Patient`(`idpatient`),
FOREIGN KEY(`iddoctor`) REFERENCES `Doctor`(`iddoctor`)
);
CREATE TABLE IF NOT EXISTS `Note` (
	`id_note` integer primary key NOT NULL UNIQUE,
	`id_appointment` INTEGER NOT NULL,
	`idpatient` INTEGER NOT NULL,
	`iddoctor` INTEGER NOT NULL,
	`content` TEXT NOT NULL,
FOREIGN KEY(`id_appointment`) REFERENCES `Appointment`(`id_appointment`),
FOREIGN KEY(`idpatient`) REFERENCES `Patient`(`idpatient`),
FOREIGN KEY(`iddoctor`) REFERENCES `Doctor`(`iddoctor`)
);
CREATE TABLE IF NOT EXISTS `Image` (
	`idimage` integer primary key NOT NULL UNIQUE,
	`instanceuid` INTEGER NOT NULL,
	`studyuid` INTEGER NOT NULL,
	`seriesuid` INTEGER NOT NULL,
	`patient_dicom_id` INTEGER NOT NULL,
	`idpatient` INTEGER NOT NULL,
	`id_appointment` INTEGER NOT NULL,
	`iddoctor` INTEGER NOT NULL,
FOREIGN KEY(`idpatient`) REFERENCES `Patient`(`idpatient`),
FOREIGN KEY(`id_appointment`) REFERENCES `Appointment`(`id_appointment`),
FOREIGN KEY(`iddoctor`) REFERENCES `Doctor`(`iddoctor`)
);