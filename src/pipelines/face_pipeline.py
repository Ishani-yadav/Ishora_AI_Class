import dlib
import numpy as np
import face_recognition_models
import streamlit as st

from collections import Counter
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():

    detector = dlib.get_frontal_face_detector()

    shapePredictor = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    faceRecog = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, shapePredictor, faceRecog


def get_face_embeddings(image_np):

    detector, shapePredictor, faceRecog = load_dlib_models()

    faces = detector(image_np, 3)

    encodings = []

    for face in faces:

        shape = shapePredictor(image_np, face)

        face_descriptor = faceRecog.compute_face_descriptor(
            image_np,
            shape,
            3
        )

        encodings.append(
            np.array(face_descriptor, dtype=np.float32)
        )

    return encodings


@st.cache_resource
def get_trained_model():

    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:
        embedding = student.get("face_embedding")
        student_id = student.get("student_id")

        if embedding is not None and student_id is not None:
            X.append(embedding)
            y.append(student_id)

    if len(X) == 0:
        return None

    X = np.array(X, dtype=np.float32)
    y = np.array(y)

    unique_students = np.unique(y)

    if len(unique_students) == 1:
        return {"clf": None,"X": X,"y": y}

    lr = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(
            max_iter=2000,
            class_weight="balanced"
        ))
    ])

    svc = Pipeline([
        ("scaler", StandardScaler()),
        ("svc", SVC(
            probability=True,
            class_weight="balanced"
        ))
    ])

    knn = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(
            n_neighbors=3,
            metric="euclidean"
        ))
    ])

    voting_clf = VotingClassifier(
        estimators=[
            ("lr", lr),
            ("svc", svc),
            ("knn", knn)
        ],
        voting="soft"
    )

    voting_clf.fit(X, y)

    return {"clf": voting_clf, "X": X,"y": y}

def train_classifier():

    st.cache_resource.clear()

    model_data = get_trained_model()

    return bool(model_data)


def predict_attendance(class_image_np):

    encodings = get_face_embeddings(class_image_np)

    detected_students = {}

    model_data = get_trained_model()

    if model_data is None:
        return detected_students, [], len(encodings)

    clf = model_data["clf"]
    X_train = model_data["X"]
    y_train = model_data["y"]

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:

        if clf is not None:
            predicted_id = int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])

        student_distances = {}

        for student_id in all_students:

            student_indexes = np.where(y_train == student_id)[0]

            distances = [
                np.linalg.norm(X_train[i] - encoding)
                for i in student_indexes
            ]

            if distances:
                student_distances[student_id] = min(distances)

        if not student_distances:
            continue

        sorted_distances = sorted(student_distances.items(),key=lambda x: x[1])

        best_student_id = sorted_distances[0][0]
        best_distance = sorted_distances[0][1]

        if len(sorted_distances) > 1:
            second_best_distance = sorted_distances[1][1]
        else:
            second_best_distance = float("inf")

        distance_margin = (
            second_best_distance - best_distance
        )

        resemblance_threshold = 0.50
        minimum_gap = 0.05

        if(
            best_student_id == predicted_id
            and best_distance <= resemblance_threshold
            and distance_margin >= minimum_gap
        ):
            detected_students[best_student_id] = True

    return detected_students,all_students,len(encodings)