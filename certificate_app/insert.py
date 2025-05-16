import streamlit as st
from supabase import create_client
from datetime import datetime

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

st.title("Certificate Generator")

name = st.text_input("Name")
cert_type = st.selectbox("Certificate Type", ["Income", "Community", "Other"])
issue_date = st.date_input("Issue Date", datetime.today())

if st.button("Generate"):
    if not name:
        st.error("Please enter your name.")
    else:
        data = {
            "name": name,
            "certificate_type": cert_type,
            "issue_date": issue_date.isoformat()
        }
        res = supabase.table("certificates").insert(data).execute()
        if res.status_code == 201:
            st.success("Certificate details saved!")
        else:
            st.error("Error saving data.")
