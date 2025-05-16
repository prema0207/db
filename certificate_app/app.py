import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
from datetime import datetime

# Supabase client init
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

def insert_certificate(name, cert_type, issue_date):
    data = {
        "name": name,
        "certificate_type": cert_type,
        "issue_date": issue_date
    }
    res = supabase.table("certificates").insert(data).execute()
    return res

def generate_pdf(name, cert_type, issue_date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=20)
    pdf.cell(0, 20, "Certificate of " + cert_type, ln=1, align="C")
    pdf.set_font("Arial", size=16)
    pdf.ln(10)
    pdf.cell(0, 10, f"This is to certify that {name}", ln=1, align="C")
    pdf.cell(0, 10, f"has been issued a {cert_type} certificate", ln=1, align="C")
    pdf.cell(0, 10, f"on {issue_date}", ln=1, align="C")
    file_path = f"{name}_{cert_type}_{issue_date}.pdf"
    pdf.output(file_path)
    return file_path

def main():
    st.title("Online Certificate Generator")

    with st.form("cert_form"):
        name = st.text_input("Enter Name")
        cert_type = st.selectbox("Certificate Type", ["Income", "Community", "Other"])
        issue_date = st.date_input("Issue Date", datetime.today())
        submitted = st.form_submit_button("Generate Certificate")

    if submitted:
        if not name:
            st.error("Please enter a name.")
            return

        # Insert into DB
        insert_response = insert_certificate(name, cert_type, issue_date.isoformat())
        if insert_response.status_code == 201:
            st.success("Certificate details saved to database.")

            # Generate PDF
            pdf_file = generate_pdf(name, cert_type, issue_date.strftime("%Y-%m-%d"))
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="Download Certificate PDF",
                    data=f,
                    file_name=pdf_file,
                    mime="application/pdf"
                )
        else:
            st.error("Failed to save to database.")

if __name__ == "__main__":
    main()
