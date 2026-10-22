import time
import streamlit as st

from src.database.config import supabase
from src.database.db import enroll_student_to_subject


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):

    # ----------------------------------------
    # 1. Validate student session
    # ----------------------------------------
    student_data = st.session_state.get("student_data")

    if not isinstance(student_data, dict):
        st.error(
            "Your student session could not be found. "
            "Please close this dialog and log in again."
        )

        if st.button("Return to Login", type="primary"):
            st.session_state.pop("student_data", None)
            st.session_state.pop("login_type", None)
            st.query_params.clear()
            st.rerun()

        return

    student_id = student_data.get("student_id")

    if student_id is None:
        st.error(
            "Student ID is missing from your session. "
            "Please log in again."
        )

        if st.button("Return to Login", type="primary"):
            st.session_state.pop("student_data", None)
            st.session_state.pop("login_type", None)
            st.query_params.clear()
            st.rerun()

        return

    # ----------------------------------------
    # 2. Validate subject code
    # ----------------------------------------
    if not subject_code or not str(subject_code).strip():
        st.error("Please enter a valid subject code.")

        if st.button("Close"):
            st.query_params.clear()
            st.rerun()

        return

    subject_code = str(subject_code).strip()

    # ----------------------------------------
    # 3. Find subject in Supabase
    # ----------------------------------------
    try:
        response = (
            supabase.table("subjects")
            .select("subject_id, name")
            .eq("subject_code", subject_code)
            .execute()
        )

    except Exception as error:
        st.error(f"Could not fetch subject details: {error}")
        return

    if not response.data:
        st.error("Subject code not found. Please check the code.")

        if st.button("Close"):
            st.query_params.clear()
            st.rerun()

        return

    subject = response.data[0]
    subject_id = subject.get("subject_id")
    subject_name = subject.get("name") or "Unnamed Subject"

    # ----------------------------------------
    # 4. Check whether student is already enrolled
    # ----------------------------------------
    try:
        check = (
            supabase.table("subjects_students")
            .select("student_id")
            .eq("subject_id", subject_id)
            .eq("student_id", student_id)
            .execute()
        )

    except Exception as error:
        st.error(f"Could not check enrollment status: {error}")
        return

    if check.data:
        st.info(f"You are already enrolled in **{subject_name}**.")

        if st.button("Got it!", type="primary"):
            st.query_params.clear()
            st.rerun()

        return

    # ----------------------------------------
    # 5. Ask student to confirm enrollment
    # ----------------------------------------
    st.markdown(
        f"Would you like to enroll in **{subject_name}**?"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("No thanks!", width="stretch"):
            st.query_params.clear()
            st.rerun()

    with col2:
        if st.button(
            "Yes, Enroll now",
            type="primary",
            width="stretch"
        ):
            try:
                result = enroll_student_to_subject(
                    student_id,
                    subject_id
                )

                # If your database function explicitly returns False,
                # treat that as a failed enrollment.
                if result is False:
                    st.error(
                        "Enrollment could not be completed. "
                        "Please try again."
                    )
                    return

                st.success("Enrolled successfully!")

                time.sleep(1)

                st.query_params.clear()
                st.rerun()

            except Exception as error:
                st.error(f"Enrollment failed: {error}")
