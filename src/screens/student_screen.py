
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
from src.pipelines.voice_pipeline import get_voice_embedding

from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject,
)


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data["student_id"]

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge",
    )

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"Welcome, {student_data['name']}")

        if st.button(
            "Logout",
            type="secondary",
            key="student_logout",
        ):
            st.session_state["is_logged_in"] = False
            st.session_state.pop("student_data", None)
            st.rerun()

    st.space()

    c1, c2 = st.columns(2)

    with c1:
        st.header("Your Enrolled Subjects")

    with c2:
        if st.button(
            "Enroll in Subject",
            type="primary",
            width="stretch",
        ):
            enroll_dialog()

    st.divider()

    with st.spinner("Loading your enrolled subjects..."):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log["subject_id"]

        if sid not in stats_map:
            stats_map[sid] = {
                "total": 0,
                "attended": 0,
            }

        stats_map[sid]["total"] += 1

        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    if not subjects:
        st.info(
            "You are not enrolled in any subjects yet. "
            "Use 'Enroll in Subject' to join a class."
        )
    else:
        cols = st.columns(2)

        for i, sub_node in enumerate(subjects):
            sub = sub_node["subjects"]
            sid = sub["subject_id"]

            stats = stats_map.get(
                sid,
                {"total": 0, "attended": 0},
            )

            def unenroll_button(
                subject_id=sid,
                subject_name=sub["name"],
            ):
                if st.button(
                    "Unenroll from this course",
                    type="tertiary",
                    width="stretch",
                    icon=":material/delete_forever:",
                    key=f"unenroll_{subject_id}",
                ):
                    unenroll_student_to_subject(
                        student_id,
                        subject_id,
                    )
                    st.toast(
                        f"Unenrolled from {subject_name} successfully"
                    )
                    st.rerun()

            with cols[i % 2]:
                subject_card(
                    name=sub["name"],
                    code=sub["subject_code"],
                    section=sub["section"],
                    stats=[
                        ("📆", "Total", stats["total"]),
                        ("✅", "Attended", stats["attended"]),
                    ],
                    footer_callback=unenroll_button,
                )

    footer_dashboard()


def student_screen():
    style_background_dashboard()
    style_base_layout()

    # Show dashboard after successful login or registration.
    if "student_data" in st.session_state:
        student_dashboard()
        return

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

    # --------------------------------------------------
    # FACE LOGIN
    # --------------------------------------------------
    if login_option == "FaceID Login":
        st.subheader("Login using FaceID")

        photo_source = st.camera_input(
            "Position your face in the center",
            key="student_login_camera",
        )

        if photo_source is not None:
            img = np.array(
                Image.open(photo_source).convert("RGB")
            )

            with st.spinner("AI is scanning..."):
                detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning("Face not found. Please try again.")

            elif num_faces > 1:
                st.warning(
                    "Multiple faces found. Please keep only "
                    "your face in the camera."
                )

            elif detected:
                student_id = int(list(detected.keys())[0])
                all_students = get_all_students()

                student = next(
                    (
                        s for s in all_students
                        if int(s["student_id"]) == student_id
                    ),
                    None,
                )

                if student:
                    st.session_state["student_data"] = student
                    st.session_state["user_role"] = "student"
                    st.session_state["is_logged_in"] = True

                    st.toast(f"Welcome back, {student['name']}!")
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

    # --------------------------------------------------
    # VOICE LOGIN
    # --------------------------------------------------
    elif login_option == "Voice Login":
        st.subheader("Login using Voice")
        st.info(
            "Voice login requires a previously enrolled voice profile."
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
                st.warning(
                    "Audio recording is working, but voice authentication "
                    "is not connected yet. It needs a function to compare "
                    "your voice embedding with saved student embeddings."
                )

    # --------------------------------------------------
    # NEW STUDENT SIGNUP
    # --------------------------------------------------
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

                                except Exception as voice_error:
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
                                train_classifier()

                                student = response_data[0]

                                st.session_state["student_data"] = student
                                st.session_state["user_role"] = "student"
                                st.session_state["is_logged_in"] = True

                                st.toast(f"Welcome, {new_name.strip()}!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(
                                    "Account creation failed. "
                                    "Please try again."
                                )

                except Exception as e:
                    st.error(f"Could not create student account: {e}")

    footer_dashboard()
