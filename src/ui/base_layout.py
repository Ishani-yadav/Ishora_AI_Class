import streamlit as st

def style_background_home():

    st.markdown("""
            <style>
                .stApp {
                    min-height: 100vh;

                    background:
                        linear-gradient(
                            135deg,
                            #EAF6FF 10%,
                            #EEF3FF 100%,
                            #F3EEFF 1%
                        ) !important;

                    overflow: hidden;
                    position: relative;
                }

                .stApp div[data-testid="stColumn"]{
                    background-color:white !important;
                    padding:2rem !important;
                    border-radius:5rem !important;
                }
            </style>
        """,
        unsafe_allow_html=True
    )

def style_background_dashboard():

    st.markdown("""
            <style>
                .stApp{
                    background:#E0E3FF !important;
                }
            </style>
        """,
        unsafe_allow_html=True
    )

def style_base_layout():

    st.markdown("""
            <style>

                @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');
            
               /* Hide Top Bar of streamlit*/

               #MainMenu, footer, header{
                    visibility:hidden;
               }

               .block-container{
                    padding-top:1.5rem;
               }

               h1{
                    font-family: 'Climate Crisis',sans-serif !important;
                    font-size: 3.5rem !important; 
                    line-height: 1.1 !important;
                    margin-bottom: 0rem !important;                            
               }
                
               h2{
                    font-family: 'Climate Crisis',sans-serif !important;
                    font-size: 2rem !important; 
                    color: black !important;
                    line-height: 1.1 !important;
                    margin-bottom: 1rem !important;            
                }
                
                h3,h4,p{
                    font-family: 'Outfit',sans-serif !important;
                    
                }
                h3{
                    color: black !important;
                }
                input{
                    background-color: white !important;
                    color: black !important;
                }

                input::placeholder{
                    color: #9A9A9A !important;
                    opacity: 1 !important;
                }
                div[data-testid="stCameraInput"] label p,
                div[data-testid="stCameraInput"] small {
                    color: black !important;
                }
                div[data-testid="stAudioInput"] label p,
                div[data-testid="stAudioInput"] small {
                    color: black !important;
                }

                div[data-testid="stTextInput"] label p{
                    color: black !important;
                }
                div[data-testid="stSelectbox"] label p{
                    color: black !important;
                }
                hr {
                    border: none !important;
                    border-top: 2px solid #D0D0D0 !important;
                    margin: 2rem 0 !important;
                }

                button{
                    border-radius: 1.5rem !important;
                    background: #5865F2 !important;
                    color: white !important;
                    padding: 10px 20px !important;
                    border: none !important;
                    transition: transform 0.25s ease-in-out !important;
                }

                button[kind="secondary"]{
                    border-radius: 1.5rem !important;
                    background: #EB459E !important;
                    color: white !important;
                    padding: 10px 20px !important;
                    border: none !important;
                    transition: transform 0.25s ease-in-out !important;
                }
                button[kind="tertiary"]{
                    border-radius: 1.5rem !important;
                    background: black !important;
                    color: white !important;
                    padding: 10px 20px !important;
                    border: none !important;
                    transition: transform 0.25s ease-in-out !important;
                }

                button:hover{
                    transform:scale(1.05);
                }
                [data-testid="stDialog"] > div {
                    background: white !important;
                    color: black !important;
                }
                [data-testid="stDialog"] p {
                    color: black !important;
                }
                [data-testid="stDialog"] .stButton > button p {
                    color: white !important;
                }

            </style>
        """,
        unsafe_allow_html=True
    )