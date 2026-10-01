import streamlit as st
import base64


def get_logo_base64():
    with open("logo.png", "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def footer_home():

    logo = get_logo_base64()

    st.markdown(
        f"""
        <div style="
            margin-top: 2rem;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
        ">
            <p style="
                color: black;
                margin: 0;
                font-size: 14px;
            ">
                Created with ❤️ by
            </p>

            <img 
                src="data:image/png;base64,{logo}"
                style="
                    height: 35px;
                    width: auto;
                    object-fit: contain;
                "
            />
        </div>
        """,
        unsafe_allow_html=True
    )


def footer_dashboard():

    logo = get_logo_base64()

    st.markdown(
        f"""
        <div style="
            margin-top: 2rem;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
        ">
            <p style="
                color: black;
                margin: 0;
                font-size: 14px;
            ">
                Created with ❤️ by
            </p>

            <img 
                src="data:image/png;base64,{logo}"
                style="
                    height: 35px;
                    width: auto;
                    object-fit: contain;
                "
            />
        </div>
        """,
        unsafe_allow_html=True
    )