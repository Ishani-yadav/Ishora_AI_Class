
import streamlit as st
from pathlib import Path
import base64


BASE_DIR = Path(__file__).resolve().parents[2]
LOGO_PATH = BASE_DIR / "logo.png"


def render_footer():
    try:
        with open(LOGO_PATH, "rb") as image_file:
            logo = base64.b64encode(
                image_file.read()
            ).decode("utf-8")
    except Exception as error:
        st.error(f"Could not load footer logo: {error}")
        return

    st.divider()

    st.markdown(
    f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 3px;
        width: 100%;
        padding: 12px 0 24px 0;
        margin: 0;
        box-sizing: border-box;
    ">
        <span style="
            color: #17234F;
            font-size: 15px;
            font-weight: 600;
            white-space: nowrap;
            margin: 0;
        ">Created with ❤️ by</span>
        <img
            src="data:image/png;base64,{logo}"
            alt="Ishani Yadav logo"
            style="
                width: 110px;
                height: 40px;
                object-fit: contain;
                display: block;
                margin: 0;
                padding: 0;
            "
        />
    </div>
    """,
    unsafe_allow_html=True,
)



def footer_home():
    render_footer()


def footer_dashboard():
    render_footer()
