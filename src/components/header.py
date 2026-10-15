import streamlit as st

def header_home():
    logo_url = "https://imgs.search.brave.com/nn0vWgrqwbB-BFhhb1Uh45KDTNuepnm9N_M8KivT5Gc/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pbWcu/bWFnbmlmaWMuY29t/L2ZyZWUtdmVjdG9y/L3ZlY3Rvci12aW50/YWdlLWNhbWVyYV81/Mzg3Ni0zNjY4MC5q/cGc_c2VtdD1haXNf/aHlicmlkJnc9NzQw/JnE9ODA"

    st.markdown(
        f"""
        <div style="
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            gap:3px;
            margin:0 0 8px 0;
            padding:0;
        ">
            <img
                src="{logo_url}"
                alt="Ishora AI Class Logo"
                style="
                    width:60px;
                    height:60px;
                    object-fit:contain;
                    display:block;
                "
            />
            <h1 style="
                text-align:center;
                color:#17234F;
                font-size:1.6rem;
                line-height:1.05;
                margin:0;
                padding:0;
            ">ISHORA AI<br>CLASS</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )


def header_dashboard():
    logo_url = "https://imgs.search.brave.com/nn0vWgrqwbB-BFhhb1Uh45KDTNuepnm9N_M8KivT5Gc/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pbWcu/bWFnbmlmaWMuY29t/L2ZyZWUtdmVjdG9y/L3ZlY3Rvci12aW50/YWdlLWNhbWVyYV81/Mzg3Ni0zNjY4MC5q/cGc_c2VtdD1haXNf/aHlicmlkJnc9NzQw/JnE9ODA"

    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            justify-content:center;
            gap:7px;
            margin:0;
            padding:0;
        ">
            <img
                src="{logo_url}"
                alt="Ishora AI Class Logo"
                style="
                    width:48px;
                    height:48px;
                    object-fit:contain;
                    display:block;
                "
            />
            <div style="
                text-align:left;
                color:#5865F2;
                font-family:sans-serif;
                font-size:1.25rem;
                font-weight:700;
                line-height:1.05;
                margin:0;
                padding:0;
            ">ISHORA AI<br>CLASS</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
