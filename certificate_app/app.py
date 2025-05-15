import streamlit as st
import mysql.connector
from datetime import datetime
import qrcode
from io import BytesIO
import base64
from jinja2 import Environment, FileSystemLoader
import pdfkit
import os

# DB connection from Streamlit secrets
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"].get("port", 3306)
    )

# Create table if not exists
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
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Generate QR code as base64 string
def generate_qr_code(data: str) -> str:
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Render HTML from template and data
def render_html(name, cert_type, income, community, date, qr_code_b64):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('certificate.html')
    html = template.render(
        name=name,
        certificate_type=cert_type,
        income=income,
        community=community,
        date=date,
        qr_code=qr_code_b64
    )
    return html

# Generate PDF from HTML string
def generate_pdf(html_str, output_path):
    config = pdfkit.configuration()  # Adjust if wkhtmltopdf path needed
    pdfkit.from_string(html_str, output_path, configuration=config)

# Streamlit app
def main():
    st.title("Online Certificate Generator")

    create_table()

    cert_type = st.selectbox("Certificate Type", ["Income", "Community"])
    name = st.text_input("Full Name")

    income = None
    community = None
    if cert_type == "Income":
        income = st.number_input("Annual Income (₹)", min_value=0.0, step=1000.0)
    else:
        community = st.text_input("Community")

    if st.button("Generate Certificate"):
        if not name.strip():
            st.error("Please enter your name.")
            return
        if cert_type == "Income" and income is None:
            st.error("Please enter income.")
            return
        if cert_type == "Community" and not community.strip():
            st.error("Please enter community.")
            return

        # Insert into DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO certificates (name, certificate_type, income, community)
            VALUES (%s, %s, %s, %s)
        """, (name, cert_type, income if income else None, community if community else None))
        conn.commit()
        cert_id = cursor.lastrowid
        cursor.close()
        conn.close()

        # Prepare certificate data
        date_str = datetime.now().strftime("%Y-%m-%d")
        verify_url = f"http://yourdomain.com/verify?id={cert_id}"
        qr_code_b64 = generate_qr_code(verify_url)

        # Render HTML & generate PDF
        html = render_html(name, cert_type, income, community, date_str, qr_code_b64)
        pdf_path = f"certificate_{cert_id}.pdf"
        generate_pdf(html, pdf_path)

        # Let user download
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        b64_pdf = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="certificate_{cert_id}.pdf">Download your certificate PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

        # Cleanup generated PDF
        os.remove(pdf_path)

if __name__ == "__main__":
    main()
