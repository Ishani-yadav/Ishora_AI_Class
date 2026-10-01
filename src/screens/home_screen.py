import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout,style_background_home

def home_screen():

    style_base_layout()
    style_background_home()

    header_home()


    st.markdown("""
        <style>

        div[data-testid="stColumn"]:has(.student-card-marker),
        div[data-testid="stColumn"]:has(.teacher-card-marker){
            background: white !important;
            padding: 30px !important;
            border-radius: 35px !important;

            box-shadow:
                0 10px 20px rgba(0,0,0,0.08),
                0 25px 45px rgba(36,136,242,0.15) !important;

            transition: 0.3s ease !important;
        }

        div[data-testid="stColumn"]:has(.student-card-marker):hover,
        div[data-testid="stColumn"]:has(.teacher-card-marker):hover{
            transform: translateY(-8px) !important;

            box-shadow:
                0 15px 25px rgba(0,0,0,0.10),
                0 30px 55px rgba(36,136,242,0.22) !important;
        }
        div[data-testid="stColumn"]:has(.teacher-card-marker) button {
            background: #7C3AED !important;
            color: white !important;
        }

        </style>
        """, unsafe_allow_html=True)
    col1,col2 = st.columns(2,gap='large')

    with col1:
        st.markdown(
            '<div class="student-card-marker"></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<h2><span style="color:#17234F;">I\'m</span> <span style="color:#2488F2;">Student</span></h2>',
            unsafe_allow_html=True
        )
        st.image("student.png", width=100)
        if st.button('Student Portal',type='primary',icon=':material/arrow_outward:',icon_position='right'):
            st.session_state['login_type'] = 'student'
            st.rerun()

    with col2:
        st.markdown(
            '<div class="teacher-card-marker"></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<h2><span style="color:#17234F;">I\'m</span> <span style="color:#7C3AED;">Teacher</span></h2>',
            unsafe_allow_html=True
        )
        st.image("teacher.png", width=100)
        if st.button('Teacher Portal',type='primary',icon=':material/arrow_outward:',icon_position='right'):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    footer_home()