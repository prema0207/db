import streamlit as st
import mysql.connector
from datetime import datetime
import pdfkit
import os

# --- Database connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",       # change to your host or Supabase host
        user="root",            # your DB username
        password="",            # your DB password
        database="certificates_db"  # your DB name
    )

# --- Create table if not exists ---
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            certificate_type VARCHAR(50),
            income DECIMAL(10,2),
            community VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# --- Generate HTML template ---
def generate_html(name, cert_type, income, community):
    date_str = datetime.now().strftime("%Y-%m-%d")
    if cert_type == "Income":
        content = f"""
        <h2 style='text-align:center;'>Income Certificate</h2>
        <p>This is to certify that <strong>{name}</strong> has an annual income of ₹{income}.</p>
        <p>Date of Issue: {date_str}</p>
        """
    else:
        content = f"""
        <h2 style='text-align:center;'>Community Certificate</h2>
        <p>This is to certify that <strong>{name}</strong> belongs to the <strong>{community}</strong> community.</p>
        <p>Date of Issue: {date_str}</p>
        """
    return f"<html><body>{content}</body></html>"

# --- Generate PDF ---
def create_pdf(html_str, output_path):
    with open("temp.html", "w") as file:
        file.write(html_str)
    pdfkit.from_file("temp.html", output_path)
    os.remove("temp.html")

# --- Streamlit App ---
def main():
    st.set_page_config(page_title="Certificate Generator")
    st.title("Online Certificate Generator")

    create_table()

    name = st.text_input("Full Name")
    cert_type = st.selectbox("Certificate Type", ["Income", "Community"])

    income = 0.0
    community = ""

    if cert_type == "Income":
        income = st.number_input("Annual Income (₹)", min_value=0.0)
    else:
        community = st.text_input("Community")

    if st.button("Generate Certificate"):
        if not name:
            st.warning("Please enter the name.")
            return
        if cert_type == "Income" and income <= 0:
            st.warning("Please enter valid income.")
            return
        if cert_type == "Community" and not community:
            st.warning("Please enter community.")
            return

        # Save to DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO certificates (name, certificate_type, income, community)
            VALUES (%s, %s, %s, %s)
        """, (name, cert_type, income if cert_type == "Income" else None, community if cert_type == "Community" else None))
        conn.commit()
        cursor.close()
        conn.close()

        # Create certificate
        html_str = generate_html(name, cert_type, income, community)
        pdf_path = f"{name}_{cert_type}_certificate.pdf"
        create_pdf(html_str, pdf_path)

        st.success("Certificate Generated Successfully!")
        with open(pdf_path, "rb") as f:
            st.download_button("Download Certificate PDF", f, file_name=pdf_path)

if __name__ == "__main__":
    main()
