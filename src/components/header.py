import streamlit as st

def header_home():

    logo_url = "https://imgs.search.brave.com/nn0vWgrqwbB-BFhhb1Uh45KDTNuepnm9N_M8KivT5Gc/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pbWcu/bWFnbmlmaWMuY29t/L2ZyZWUtdmVjdG9y/L3ZlY3Rvci12aW50/YWdlLWNhbWVyYV81/Mzg3Ni0zNjY4MC5q/cGc_c2VtdD1haXNf/aHlicmlkJnc9NzQw/JnE9ODA"

    st.markdown(f"""
        <div style='display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:2rem '>
            <img src='{logo_url}' style='border-radius:30%; height:100px;'/>
            <h1 style='text-align:center; color: #17234F'> Ishora AI  <br> CLASS</h1>
        </div>
        
    """,unsafe_allow_html=True)

def header_dashboard():

    logo_url = "https://imgs.search.brave.com/nn0vWgrqwbB-BFhhb1Uh45KDTNuepnm9N_M8KivT5Gc/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pbWcu/bWFnbmlmaWMuY29t/L2ZyZWUtdmVjdG9y/L3ZlY3Rvci12aW50/YWdlLWNhbWVyYV81/Mzg3Ni0zNjY4MC5q/cGc_c2VtdD1haXNf/aHlicmlkJnc9NzQw/JnE9ODA"

    st.markdown(f"""
        <div style='display:flex; align-items:center; justify-content:center; gap:10px;'>
            <img src='{logo_url}' style='border-radius:30%; height:85px;'/>
            <div style='text-align:left;color:#5865F2;font-family:"Climate Crisis", sans-serif;font-size:2rem;line-height:1.1;'>
                SNAP SHOT <br>CLASS
            </div>
        </div>
    """, unsafe_allow_html=True)