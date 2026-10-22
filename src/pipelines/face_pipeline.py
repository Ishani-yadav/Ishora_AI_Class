
import dlib
import numpy as np
import face_recognition_models
import streamlit as st

from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from src.database.db import get_all_students


# --------------------------------------------------
# 1. LOAD DLIB MODELS
# --------------------------------------------------

@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    shape_predictor = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    face_recognition_model = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, shape_predictor, face_recognition_model


# --------------------------------------------------
# 2. EXTRACT FACE EMBEDDINGS
# --------------------------------------------------

def get_face_embeddings(image_np):
    """
    Input:
        RGB image as a NumPy array.

    Output:
        List of 128-dimensional face embeddings.
    """

    if image_np is None:
        return []

    image_np = np.asarray(image_np)

    if image_np.ndim != 3 or image_np.shape[2] != 3:
        return []

    # Ensure the image is compatible with Dlib.
    if image_np.dtype != np.uint8:
        image_np = np.clip(image_np, 0, 255).astype(np.uint8)

    detector, shape_predictor, face_recognition_model = (
        load_dlib_models()
    )

    # Upsampling can help detect smaller faces in classroom photos.
    detected_faces = detector(image_np, 1)

    embeddings = []

    for face in detected_faces:
        try:
            shape = shape_predictor(image_np, face)

            descriptor = (
                face_recognition_model.compute_face_descriptor(
                    image_np,
                    shape,
                    1
                )
            )

            embedding = np.asarray(
                descriptor,
                dtype=np.float32
            )

            if embedding.shape == (128,):
                embeddings.append(embedding)

        except Exception as error:
            print(f"Could not extract face embedding: {error}")

    return embeddings


# --------------------------------------------------
# 3. LOAD STUDENT EMBEDDINGS AND TRAIN CLASSIFIER
# --------------------------------------------------

@st.cache_resource
def get_trained_model():
    """
    Loads enrolled student embeddings from the database.

    Each database face_embedding must contain 128 numbers.
    """

    students = get_all_students()

    if not students:
        return None

    embeddings = []
    student_ids = []

    for student in students:
        student_id = student.get("student_id")
        embedding = student.get("face_embedding")

        if student_id is None or embedding is None:
            continue

        try:
            embedding = np.asarray(
                embedding,
                dtype=np.float32
            )

            if embedding.shape != (128,):
                print(
                    f"Skipping student {student_id}: "
                    f"expected 128 embedding values, "
                    f"received shape {embedding.shape}"
                )
                continue

            if not np.all(np.isfinite(embedding)):
                print(
                    f"Skipping student {student_id}: "
                    "embedding contains invalid values."
                )
                continue

            embeddings.append(embedding)
            student_ids.append(student_id)

        except (TypeError, ValueError) as error:
            print(
                f"Invalid embedding for student "
                f"{student_id}: {error}"
            )

    if not embeddings:
        return None

    X = np.asarray(embeddings, dtype=np.float32)
    y = np.asarray(student_ids)

    unique_students = np.unique(y)

    # A classifier cannot distinguish classes if only one
    # unique student is enrolled. Distance matching can still work.
    if len(unique_students) < 2:
        return {
            "clf": None,
            "X": X,
            "y": y
        }

    # Keep classifier selection safe for small datasets.
    classifiers = []

    logistic_regression = Pipeline([
        ("scaler", StandardScaler()),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced"
            )
        )
    ])

    classifiers.append(("lr", logistic_regression))

    svm = Pipeline([
        ("scaler", StandardScaler()),
        (
            "classifier",
            SVC(
                probability=True,
                class_weight="balanced"
            )
        )
    ])

    classifiers.append(("svm", svm))

    # KNN requires at least three training samples for k=3.
    if len(X) >= 3:
        knn = Pipeline([
            ("scaler", StandardScaler()),
            (
                "classifier",
                KNeighborsClassifier(
                    n_neighbors=min(3, len(X)),
                    metric="euclidean"
                )
            )
        ])

        classifiers.append(("knn", knn))

    try:
        if len(classifiers) == 1:
            classifier = classifiers[0][1]
        else:
            classifier = VotingClassifier(
                estimators=classifiers,
                voting="soft"
            )

        classifier.fit(X, y)

        return {
            "clf": classifier,
            "X": X,
            "y": y
        }

    except Exception as error:
        # Distance matching can still operate if training fails.
        print(f"Classifier training failed: {error}")

        return {
            "clf": None,
            "X": X,
            "y": y
        }


# --------------------------------------------------
# 4. CLEAR CACHE AND RETRAIN
# --------------------------------------------------

def train_classifier():
    """
    Call after enrolling a student or updating their
    face embedding so the latest database data is loaded.
    """

    get_trained_model.clear()

    model_data = get_trained_model()

    return model_data is not None


# --------------------------------------------------
# 5. RECOGNIZE FACES IN A CLASSROOM IMAGE
# --------------------------------------------------

def predict_attendance(class_image_np):
    """
    Returns:
        detected_students: {student_id: True}
        all_students: list of enrolled student IDs
        face_count: number of detected faces

    A face is matched using the closest stored embedding
    and a distance threshold. Classifier disagreement is
    logged but does not automatically reject the match.
    """

    encodings = get_face_embeddings(class_image_np)

    detected_students = {}

    model_data = get_trained_model()

    if model_data is None:
        print("No valid student face embeddings found.")
        return detected_students, [], len(encodings)

    classifier = model_data["clf"]
    X_train = model_data["X"]
    y_train = model_data["y"]

    all_students = sorted(
        set(y_train.tolist()),
        key=str
    )

    # Dlib embeddings normally have Euclidean distances
    # that should be evaluated on your actual images.
    # Start with a conservative threshold and tune it
    # using known students and unknown faces.
    resemblance_threshold = 0.50
    minimum_gap = 0.05

    for face_number, encoding in enumerate(encodings, start=1):

        # Find the minimum distance from this face to
        # each student's stored embeddings.
        student_distances = {}

        for student_id in all_students:
            indexes = np.where(y_train == student_id)[0]

            distances = [
                float(np.linalg.norm(X_train[i] - encoding))
                for i in indexes
            ]

            if distances:
                student_distances[student_id] = min(distances)

        if not student_distances:
            continue

        sorted_distances = sorted(
            student_distances.items(),
            key=lambda item: item[1]
        )

        best_student_id = sorted_distances[0][0]
        best_distance = sorted_distances[0][1]

        if len(sorted_distances) > 1:
            second_best_distance = sorted_distances[1][1]
        else:
            second_best_distance = float("inf")

        distance_margin = (
            second_best_distance - best_distance
        )

        predicted_id = None

        if classifier is not None:
            try:
                predicted_id = classifier.predict(
                    encoding.reshape(1, -1)
                )[0]
            except Exception as error:
                print(f"Classifier prediction failed: {error}")

        # Debugging output: check the Streamlit terminal.
        print(f"\nFace {face_number}")
        print(f"Classifier prediction: {predicted_id}")
        print(f"Closest student: {best_student_id}")
        print(f"Best distance: {best_distance:.4f}")
        print(
            f"Second-best distance: "
            f"{second_best_distance:.4f}"
        )
        print(f"Distance margin: {distance_margin:.4f}")

        # A small distance means the face is close to a
        # stored embedding. The margin helps avoid ambiguous
        # matches when two students look similarly close.
        distance_is_good = (
            best_distance <= resemblance_threshold
        )

        margin_is_good = (
            len(sorted_distances) == 1
            or distance_margin >= minimum_gap
        )

        if distance_is_good and margin_is_good:
            detected_students[best_student_id] = True

            print(f"Recognized student: {best_student_id}")
        else:
            print("Face rejected: distance or margin check failed.")

    return detected_students, all_students, len(encodings)
