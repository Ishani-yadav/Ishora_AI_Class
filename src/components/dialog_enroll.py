
import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write("Enter the subject code provided by your teacher to enroll.")

    join_code = st.text_input(
        "Subject Code",
        placeholder="Eg. CS101"
    ).strip()

    if st.button("Enroll now", type="primary", width="stretch"):
        if not join_code:
            st.warning("Please enter a subject code.")
            return

        try:
            # Find the subject
            res = (
                supabase.table("subjects")
                .select("subject_id, name, subject_code")
                .eq("subject_code", join_code)
                .execute()
            )

            if not res.data:
                st.error("Invalid subject code. Please check with your teacher.")
                return

            subject = res.data[0]
            student_id = st.session_state.student_data["student_id"]

            # Check whether the student is already enrolled
            check = (
                supabase.table("subjects_students")
                .select("subject_id")
                .eq("subject_id", subject["subject_id"])
                .eq("student_id", student_id)
                .execute()
            )

            if check.data:
                st.warning("You are already enrolled in this subject.")
                return

            # Enroll the student
            enroll_student_to_subject(
                student_id,
                subject["subject_id"]
            )

            st.success(f"Successfully enrolled in {subject['name']}!")
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"Enrollment failed: {e}")
