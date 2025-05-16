import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pdfkit

# Supabase credentials from secrets
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]

# Supabase client
supabase: Client = create_client(url, key)

# Function to insert data
def insert_data(data):
    response = supabase.table("certificates").insert(data).execute()
    return response

# Streamlit form
def main():
    st.title("Online Certificate Generator")

    with st.form("certificate_form"):
        name = st.text_input("Name")
        purpose = st.text_input("Purpose")
        submit = st.form_submit_button("Generate Certificate")

        if submit:
            data = {
                "name": name,
                "purpose": purpose,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            insert_data(data)
            st.success("Certificate saved to database!")

if __name__ == "__main__":
    main()
