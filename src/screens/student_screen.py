
import streamlit as st
import numpy as np
import time

from PIL import Image

from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout,
)
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card

from src.pipelines.face_pipeline import (
    predict_attendance,
    get_face_embeddings,
    train_classifier,
)

from src.pipelines.voice_pipeline import (
    get_voice_embedding,
    identify_speaker,
)

from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject,
)


# ==================================================
# STUDENT DASHBOARD
# ==================================================

def student_dashboard():
    student_data = st.session_state.get("student_data")

    # Validate the current student session.
    if not isinstance(student_data, dict):
        st.error("Your student session has expired. Please log in again.")
        st.session_state["is_logged_in"] = False
        st.session_state["user_role"] = None
        st.session_state.pop("student_data", None)
        st.rerun()
        return

    student_id = student_data.get("student_id")

    if student_id is None:
        st.error("Student ID is missing. Please log in again.")
        st.session_state["is_logged_in"] = False
        st.session_state["user_role"] = None
        st.session_state.pop("student_data", None)
        st.rerun()
        return

    # Header and logout.
    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge",
    )

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"Welcome, {student_data.get('name', 'Student')}")

        if st.button(
            "Logout",
            type="secondary",
            key="student_logout",
        ):
            st.session_state["is_logged_in"] = False
            st.session_state["user_role"] = None
            st.session_state.pop("student_data", None)
            st.rerun()

    st.space()

    # Subject heading and enrollment button.
    c1, c2 = st.columns(2)

    with c1:
        st.header("Your Enrolled Subjects")

    with c2:
        if st.button(
            "Enroll in Subject",
            type="primary",
            width="stretch",
            key="student_enroll_subject",
        ):
            enroll_dialog()

    st.divider()

    # Load subjects and attendance.
    try:
        with st.spinner("Loading your enrolled subjects..."):
            subjects = get_student_subjects(student_id) or []
            logs = get_student_attendance(student_id) or []

    except Exception as error:
        st.error(f"Could not load your dashboard: {error}")
        footer_dashboard()
        return

    # Calculate attendance statistics for each subject.
    stats_map = {}

    for log in logs:
        sid = log.get("subject_id")

        if sid is None:
            continue

        if sid not in stats_map:
            stats_map[sid] = {
                "total": 0,
                "attended": 0,
            }

        stats_map[sid]["total"] += 1

        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    # Display enrolled subjects.
    if not subjects:
        st.info(
            "You are not enrolled in any subjects yet. "
            "Use 'Enroll in Subject' to join a class."
        )

    else:
        cols = st.columns(2)

        for i, sub_node in enumerate(subjects):
            sub = sub_node.get("subjects")

            if not isinstance(sub, dict):
                st.warning(
                    "A subject record could not be loaded. "
                    "Please check your database relationship."
                )
                continue

            sid = sub.get("subject_id")

            if sid is None:
                continue

            stats = stats_map.get(
                sid,
                {"total": 0, "attended": 0},
            )

            def unenroll_button(
                subject_id=sid,
                subject_name=sub.get("name", "Subject"),
            ):
                if st.button(
                    "Unenroll from this course",
                    type="tertiary",
                    width="stretch",
                    icon=":material/delete_forever:",
                    key=f"unenroll_{subject_id}",
                ):
                    try:
                        unenroll_student_to_subject(
                            student_id,
                            subject_id,
                        )

                        st.toast(
                            f"Unenrolled from {subject_name} successfully."
                        )
                        st.rerun()

                    except Exception as error:
                        st.error(f"Could not unenroll: {error}")

            with cols[i % 2]:
                subject_card(
                    name=sub.get("name", "Unnamed Subject"),
                    code=sub.get("subject_code", ""),
                    section=sub.get("section", ""),
                    stats=[
                        ("📆", "Total", stats["total"]),
                        ("✅", "Attended", stats["attended"]),
                    ],
                    footer_callback=unenroll_button,
                )

    footer_dashboard()


# ==================================================
# STUDENT SCREEN
# ==================================================

def student_screen():
    style_background_dashboard()
    style_base_layout()

    # Initialize session state.
    if "student_data" not in st.session_state:
        st.session_state["student_data"] = None

    if "user_role" not in st.session_state:
        st.session_state["user_role"] = None

    if "is_logged_in" not in st.session_state:
        st.session_state["is_logged_in"] = False

    # Open dashboard only after successful student login.
    student_data = st.session_state.get("student_data")

    if (
        st.session_state["is_logged_in"]
        and st.session_state["user_role"] == "student"
        and isinstance(student_data, dict)
        and student_data.get("student_id") is not None
    ):
        student_dashboard()
        return

    # Student portal header.
    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge",
    )

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Go back to Home",
            type="secondary",
            key="student_home_back",
        ):
            st.session_state["login_type"] = None
            st.rerun()

    st.space()
    st.space()

    st.header("Student Portal", text_alignment="center")

    login_option = st.radio(
        "Choose an option",
        [
            "FaceID Login",
            "Voice Login",
            "New Student Signup",
        ],
        horizontal=True,
        key="student_portal_option",
    )

    # ----------------------------------------------
    # FACE ID LOGIN
    # ----------------------------------------------

    if login_option == "FaceID Login":
        st.subheader("Login using FaceID")

        photo_source = st.camera_input(
            "Position your face in the center",
            key="student_login_camera",
        )

        if photo_source is not None:
            try:
                img = np.array(
                    Image.open(photo_source).convert("RGB")
                )

                with st.spinner("AI is scanning..."):
                    detected, all_ids, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.warning(
                        "Face not found. Please try again with "
                        "good lighting."
                    )

                elif num_faces > 1:
                    st.warning(
                        "Multiple faces found. Please keep only "
                        "your face in the camera."
                    )

                elif detected:
                    student_id = list(detected.keys())[0]

                    all_students = get_all_students() or []

                    student = next(
                        (
                            s for s in all_students
                            if str(s.get("student_id")) == str(student_id)
                        ),
                        None,
                    )

                    if student:
                        st.session_state["student_data"] = student
                        st.session_state["user_role"] = "student"
                        st.session_state["is_logged_in"] = True

                        st.toast(
                            f"Welcome back, {student.get('name', 'Student')}!"
                        )
                        time.sleep(1)
                        st.rerun()

                    else:
                        st.error(
                            "Your face was recognized, but your "
                            "student profile was not found."
                        )

                else:
                    st.warning(
                        "Face not recognized. If you are a new student, "
                        "choose 'New Student Signup'."
                    )

            except Exception as error:
                st.error(f"Face login failed: {error}")

    # ----------------------------------------------
    # VOICE LOGIN
    # ----------------------------------------------


    elif login_option == "Voice Login":
        st.subheader("Login using Voice")

        st.info(
            "Record your voice using the same language and "
            "a similar phrase you used during signup."
        )

        audio_login = st.audio_input(
            "Record your voice",
            key="student_voice_login",
        )

        if st.button(
            "Login with Voice",
            type="primary",
            key="student_voice_login_button",
        ):
            if audio_login is None:
                st.warning("Please record your voice first.")

            else:
                try:
                    with st.spinner("Checking your voice..."):
                        new_embedding = get_voice_embedding(
                            audio_login.getvalue()
                        )

                        if new_embedding is None:
                            st.error(
                                "Could not process your recording. "
                                "Please record again in a quiet place."
                            )
                        else:
                            all_students = get_all_students() or []

                            candidates = {}

                            for student in all_students:
                                stored = student.get("voice_embedding")

                                if stored is not None:
                                    try:
                                        stored = np.asarray(
                                            stored, dtype=np.float32
                                        )

                                        if (
                                            stored.ndim == 1
                                            and stored.size > 0
                                            and np.all(np.isfinite(stored))
                                        ):
                                            candidates[
                                                student["student_id"]
                                            ] = stored.tolist()

                                    except (TypeError, ValueError):
                                        continue

                            if not candidates:
                                st.error(
                                    "No enrolled voice profiles found. "
                                    "Please register a voice during signup."
                                )
                            else:
                                student_id, score = identify_speaker(
                                    new_embedding,
                                    candidates,
                                    threshold=0.65,
                                )

                                st.caption(
                                    f"Voice similarity score: {score:.3f}"
                                )

                                if student_id is None:
                                    st.error(
                                        "Voice not recognized. "
                                        "Please try again."
                                    )
                                else:
                                    student = next(
                                        (
                                            s for s in all_students
                                            if str(s.get("student_id"))
                                            == str(student_id)
                                        ),
                                        None,
                                    )

                                    if student is None:
                                        st.error(
                                            "The matching student profile "
                                            "could not be loaded."
                                        )
                                    else:
                                        st.session_state["student_data"] = student
                                        st.session_state["user_role"] = "student"
                                        st.session_state["is_logged_in"] = True

                                        st.toast(
                                            f"Welcome back, "
                                            f"{student.get('name', 'Student')}!"
                                        )
                                        time.sleep(1)
                                        st.rerun()

                except Exception as error:
                    st.error(f"Voice login failed: {error}")


    # ----------------------------------------------
    # NEW STUDENT SIGNUP
    # ----------------------------------------------

    elif login_option == "New Student Signup":
        st.subheader("Register a New Student")

        new_name = st.text_input(
            "Enter your full name",
            placeholder="E.g. Ishani Yadav",
            key="new_student_name",
        )

        photo_source = st.camera_input(
            "Capture your face for registration",
            key="student_signup_camera",
        )

        st.subheader("Optional: Voice Enrollment")

        st.caption(
            "You can enroll your voice now if you want to use "
            "voice-based attendance in the future."
        )

        audio_data = st.audio_input(
            "Record a short phrase, such as: "
            "My name is Ishani Yadav, I am present.",
            key="student_signup_voice",
        )

        if st.button(
            "Create Account",
            type="primary",
            key="create_student_account",
        ):
            if not new_name.strip():
                st.warning("Please enter your name.")

            elif photo_source is None:
                st.warning(
                    "Please capture your face before creating your account."
                )

            else:
                try:
                    with st.spinner("Creating your profile..."):
                        img = np.array(
                            Image.open(photo_source).convert("RGB")
                        )

                        encodings = get_face_embeddings(img)

                        if not encodings:
                            st.error(
                                "Couldn't capture your facial features. "
                                "Please try another photo with good lighting."
                            )

                        else:
                            face_emb = encodings[0].tolist()
                            voice_emb = None

                            if audio_data is not None:
                                try:
                                    voice_emb = get_voice_embedding(
                                        audio_data.getvalue()
                                    )

                                    if hasattr(voice_emb, "tolist"):
                                        voice_emb = voice_emb.tolist()

                                except Exception:
                                    st.warning(
                                        "Voice enrollment failed. "
                                        "Your account will be created "
                                        "without a voice profile."
                                    )
                                    voice_emb = None

                            response_data = create_student(
                                new_name.strip(),
                                face_embedding=face_emb,
                                voice_embedding=voice_emb,
                            )

                            if response_data:
                                student = response_data[0]

                                # Save the new student session before rerun.
                                st.session_state["student_data"] = student
                                st.session_state["user_role"] = "student"
                                st.session_state["is_logged_in"] = True

                                # Refresh classifier after inserting new data.
                                train_classifier()

                                st.toast(
                                    f"Welcome, {new_name.strip()}!"
                                )
                                time.sleep(1)
                                st.rerun()

                            else:
                                st.error(
                                    "Account creation failed. "
                                    "Please try again."
                                )

                except Exception as error:
                    st.error(
                        f"Could not create student account: {error}"
                    )

    footer_dashboard()
