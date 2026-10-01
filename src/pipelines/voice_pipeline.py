from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import io
import librosa
import streamlit as st


@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()


def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()

        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=17000,
            mono=True
        )

        if len(audio) == 0:
            st.warning("No audio detected")
            return None

        # Remove silence / normalize audio
        wav = preprocess_wav(audio)

        if len(wav) < 17000 * 0.5:
            st.warning("Voice recording is too short")
            return None

        embedding = encoder.embed_utterance(wav)

        return embedding.tolist()

    except Exception as e:
        st.error(f"Voice recognition error: {e}")
        return None


def cosine_similarity(embedding1, embedding2):

    embedding1 = np.array(embedding1, dtype=np.float32)
    embedding2 = np.array(embedding2, dtype=np.float32)

    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)

    if norm1 == 0 or norm2 == 0:
        return -1.0

    return np.dot(embedding1, embedding2) / (norm1 * norm2)


def identify_speaker(new_embedding, candidates_dict, threshold=0.65):

    if new_embedding is None or not candidates_dict:
        return None, 0.0

    best_sId = None
    best_score = -1.0

    for sId, stored_embedding in candidates_dict.items():

        if stored_embedding is None:
            continue

        similarity = cosine_similarity(
            new_embedding,
            stored_embedding
        )

        print(f"{sId} -> {similarity:.4f}")

        if similarity > best_score:
            best_score = similarity
            best_sId = sId

    if best_score >= threshold:
        return best_sId, best_score

    return None, best_score


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):

    try:
        encoder = load_voice_encoder()

        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=17000,
            mono=True
        )

        if len(audio) == 0:
            return {}

        segments = librosa.effects.split(
            audio,
            top_db=30
        )

        identified_result = {}

        for start, end in segments:

            if (end - start) < sr * 0.5:
                continue

            segment_audio = audio[start:end]

            wav = preprocess_wav(segment_audio)

            if len(wav) < sr * 0.5:
                continue

            embedding = encoder.embed_utterance(wav)

            sId, score = identify_speaker(
                embedding,
                candidates_dict,
                threshold
            )

            if sId is not None:

                if (
                    sId not in identified_result
                    or score > identified_result[sId]
                ):
                    identified_result[sId] = score

        return identified_result

    except Exception as e:

        st.error(f"Bulk process error: {e}")

        return {}