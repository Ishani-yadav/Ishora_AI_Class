
from src.database.config import supabase
import bcrypt


# -------------------- PASSWORD FUNCTIONS --------------------

def hash_pass(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def check_pass(password, hashed):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )


# -------------------- TEACHER FUNCTIONS --------------------

def check_teacher_exists(username):
    response = (
        supabase.table("teachers")
        .select("username")
        .eq("username", username)
        .execute()
    )
    return len(response.data or []) > 0


def create_teacher(username, password, name):
    data = {
        "username": username,
        "password": hash_pass(password),
        "name": name
    }

    response = supabase.table("teachers").insert(data).execute()
    return response.data or []


def teacher_login(username, password):
    response = (
        supabase.table("teachers")
        .select("*")
        .eq("username", username)
        .execute()
    )

    if response.data:
        teacher = response.data[0]

        if check_pass(password, teacher["password"]):
            return teacher

    return None


# -------------------- STUDENT FUNCTIONS --------------------

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data or []


def create_student(
    new_name,
    face_embedding=None,
    voice_embedding=None
):
    data = {
        "name": new_name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }

    response = supabase.table("students").insert(data).execute()
    return response.data or []


# -------------------- SUBJECT FUNCTIONS --------------------

def create_subject(subject_code, name, section, teacher_id):
    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id
    }

    response = supabase.table("subjects").insert(data).execute()
    return response.data or []


def get_teacher_subjects(teacher_id):
    # Fetch subjects without relying on nested foreign-key joins.
    response = (
        supabase.table("subjects")
        .select("*")
        .eq("teacher_id", teacher_id)
        .execute()
    )

    subjects = response.data or []

    for subject in subjects:
        subject_id = subject["subject_id"]

        # Count enrolled students.
        students_response = (
            supabase.table("subjects_students")
            .select("student_id", count="exact")
            .eq("subject_id", subject_id)
            .execute()
        )

        subject["total_students"] = students_response.count or 0

        # Count unique attendance sessions.
        attendance_response = (
            supabase.table("attandance_logs")
            .select("timestamp")
            .eq("subject_id", subject_id)
            .execute()
        )

        timestamps = {
            row["timestamp"]
            for row in (attendance_response.data or [])
            if row.get("timestamp") is not None
        }

        subject["total_classes"] = len(timestamps)

    return subjects


# -------------------- ENROLLMENT FUNCTIONS --------------------

def enroll_student_to_subject(student_id, subject_id):
    data = {
        "student_id": student_id,
        "subject_id": subject_id
    }

    response = (
        supabase.table("subjects_students")
        .insert(data)
        .execute()
    )

    return response.data or []


def unenroll_student_to_subject(student_id, subject_id):
    response = (
        supabase.table("subjects_students")
        .delete()
        .eq("student_id", student_id)
        .eq("subject_id", subject_id)
        .execute()
    )

    return response.data or []


def get_student_subjects(student_id):
    # Fetch enrollment records first.
    response = (
        supabase.table("subjects_students")
        .select("*")
        .eq("student_id", student_id)
        .execute()
    )

    enrollments = response.data or []

    # Fetch each subject separately to avoid nested joins.
    for enrollment in enrollments:
        subject_response = (
            supabase.table("subjects")
            .select("*")
            .eq("subject_id", enrollment["subject_id"])
            .execute()
        )

        enrollment["subjects"] = (
            subject_response.data[0]
            if subject_response.data
            else None
        )

    return enrollments




def get_student_attendance(student_id):
    # NOTE: The table name below intentionally matches
    # your existing Supabase table: attandance_logs.
    response = (
        supabase.table("attandance_logs")
        .select("*")
        .eq("student_id", student_id)
        .execute()
    )

    logs = response.data or []

    # Attach subject details without requiring a foreign-key join.
    for log in logs:
        subject_response = (
            supabase.table("subjects")
            .select("*")
            .eq("subject_id", log["subject_id"])
            .execute()
        )

        log["subjects"] = (
            subject_response.data[0]
            if subject_response.data
            else None
        )

    return logs


def create_attendance(logs):
    if not logs:
        return []

    # Use the actual table name shown in your Supabase dashboard.
    response = (
        supabase.table("attandance_logs")
        .insert(logs)
        .execute()
    )

    return response.data or []


def get_attendance_for_teacher(teacher_id):
    # Fetch this teacher's subjects first.
    subjects_response = (
        supabase.table("subjects")
        .select("*")
        .eq("teacher_id", teacher_id)
        .execute()
    )

    subjects = subjects_response.data or []
    attendance_records = []

    # Fetch logs for each subject.
    for subject in subjects:
        logs_response = (
            supabase.table("attandance_logs")
            .select("*")
            .eq("subject_id", subject["subject_id"])
            .execute()
        )

        for log in (logs_response.data or []):
            log["subjects"] = subject
            attendance_records.append(log)

    return attendance_records
