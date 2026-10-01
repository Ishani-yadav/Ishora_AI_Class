# 🤖 AiAttendance

**AiAttendance** is an AI-powered attendance management system that uses **Face Recognition** and **Voice Recognition** to identify students and manage attendance.

The application provides separate interfaces for **Students** and **Teachers**, with student identification through face recognition and optional voice-based verification.

---

## ✨ Features

### 👨‍🎓 Student

* Face-based student login
* Capture face using the camera
* Face recognition for student identification
* Register a new student profile
* Optional voice enrollment
* Voice-based student identification
* View enrolled subjects
* View attendance records

### 👨‍🏫 Teacher

* Teacher dashboard
* Create subjects
* Manage created subjects
* Generate unique subject codes
* View students enrolled in a subject
* View class statistics
* View attendance information

### 🤖 AI-Based Identification

* Face detection using Dlib
* Face embedding generation
* Face recognition using trained machine learning model
* Student identification using SVM
* Face-distance based verification
* Voice embedding generation using Resemblyzer
* Voice similarity-based student identification

---

## 🧠 Face Recognition

The face recognition pipeline works as follows:

```text
Camera Input
     ↓
Face Detection
     ↓
Face Landmark Detection
     ↓
Face Embedding Generation
     ↓
Compare with Registered Students
     ↓
Student Identification
     ↓
Face Verification
```

The system generates a numerical representation (**face embedding**) of the detected face and compares it with the registered student data.

A distance threshold is used to determine whether the detected face is a valid match.

---

## 🎙️ Voice Recognition

The project also supports voice-based student identification.

```text
Voice Input
     ↓
Audio Processing
     ↓
Voice Embedding
     ↓
Compare with Registered Voice Data
     ↓
Similarity Score
     ↓
Student Identification
```

Voice recognition is currently implemented as an **optional identification method** during student profile registration and verification.

---

## 🏫 Subject Management

Teachers can manage their subjects through the teacher dashboard.

Each subject contains a unique **subject code**, which can be used for student enrollment.

Teachers can:

* Create subjects
* View their subjects
* View enrolled students
* Check class-related statistics
* Monitor attendance information

---

## 📊 Attendance Management

Attendance data is stored in the database for each class/session.

The system can retrieve attendance records for students and display their attendance information through the student dashboard.

The attendance system is connected with the subject and student information stored in the database.

---

## 🗄️ Database

The application uses **Supabase** as its database.

The database stores information related to:

* Students
* Teachers
* Subjects
* Student-subject relationships
* Attendance records
* Student identification data

---

## 🛠️ Tech Stack

### Programming Language

* Python

### UI Framework

* Streamlit

### Machine Learning

* Scikit-learn
* SVM

### Computer Vision

* Dlib
* Face Recognition Models
* NumPy
* Pillow

### Voice Recognition

* Resemblyzer
* Librosa

### Database

* Supabase

---

## 🔄 Application Flow

### Student Flow

```text
Student
   ↓
Student Login
   ↓
Face Recognition
   ↓
Student Identified
   ↓
Student Dashboard
   ↓
View Subjects
   ↓
View Attendance
```

### New Student Flow

```text
Student
   ↓
Face Recognition
   ↓
Face Not Recognized
   ↓
Register New Profile
   ↓
Enter Student Information
   ↓
Optional Voice Enrollment
   ↓
Profile Created
```

### Teacher Flow

```text
Teacher
   ↓
Teacher Dashboard
   ↓
Create / Manage Subject
   ↓
Subject Code
   ↓
Students Enroll
   ↓
View Students
   ↓
Monitor Attendance
```

---

## 🎯 Project Objective

The main objective of AiAttendance is to automate student identification and attendance management using **Artificial Intelligence**.

The project combines:

* Computer Vision
* Face Recognition
* Voice Recognition
* Machine Learning
* Database Management
* Streamlit

to create an AI-based attendance management system.

---

## 👨‍💻 Author

**Ishani Yadav**

AiAttendance — AI-powered attendance management system built with Python, Machine Learning, Computer Vision, Voice Recognition and Streamlit.