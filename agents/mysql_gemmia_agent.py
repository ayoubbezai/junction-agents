# agents/mysql_gemmia_agent.py

import mysql.connector
import requests
from fpdf import FPDF
import os
from datetime import datetime

class MySQLGemmiaAgent:
    DEFAULT_MYSQL_CONFIG = {
        'host': '127.0.0.1',
        'port': 3306,
        'database': 'junction',
        'user': 'root',
        'password': ''
    }
    DEFAULT_GEMMIA_API_KEY = "AIzaSyCHlIBXW3UF7lUah8UtuP98-_MH_YU9nc4"

    def __init__(self, mysql_config=None, gemmia_api_key=None):
        self.mysql_config = mysql_config or self.DEFAULT_MYSQL_CONFIG.copy()
        self.gemmia_api_key = (
            gemmia_api_key or
            os.getenv('GEMMIA_API_KEY') or
            self.DEFAULT_GEMMIA_API_KEY
        )
        self.conn = None

    @classmethod
    def from_env(cls):
        config = {
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_DATABASE', 'junction'),
            'user': os.getenv('DB_USERNAME', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
        }
        return cls(mysql_config=config, gemmia_api_key=os.getenv('GEMMIA_API_KEY'))

    def connect_mysql(self):
        self.conn = mysql.connector.connect(**self.mysql_config)
        print("Connected to MySQL.")

    def fetch_data(self, query):
        if not self.conn:
            self.connect_mysql()
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_gemmia_data(self, endpoint, params=None):
        headers = {"Authorization": f"Bearer {self.gemmia_api_key}"}
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def generate_pdf_report(self, data, filename=None):
        # Ensure the pdf directory exists
        pdf_dir = os.path.join(os.path.dirname(__file__), '..', 'pdf')
        os.makedirs(pdf_dir, exist_ok=True)
        # Generate unique filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"AQUAINTEL_Gemini_Report_{timestamp}.pdf"
        filepath = os.path.join(pdf_dir, filename)

        pdf = FPDF()
        pdf.add_page()
        # Add logo (centered, width 40)
        try:
            # Use absolute path for logo
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fishtaLogo.png'))
            pdf.image(logo_path, x=(210-40)/2, y=10, w=40)
            pdf.ln(28)  # Add space below the logo
        except Exception as e:
            print(f"Could not add logo: {e}")
            pdf.ln(10)
        # Title
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 12, txt="AQUAINTEL Water Quality Report", ln=True, align="C")
        pdf.ln(2)
        # Subtitle
        pdf.set_font("Arial", 'I', 12)
        # Section Header
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt="Gemini AI Summary", ln=True, align="L")
        pdf.ln(2)
        # Summary Body (multi-line, wrapped)
        pdf.set_font("Arial", '', 12)
        summary = data[0] if data else ""
        for line in summary.split('\n'):
            pdf.multi_cell(0, 8, txt=line, align="L")
            pdf.ln(1)
        # Footer with generation date
        pdf.set_y(-20)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 0, 'C')
        pdf.output(filepath)
        print(f"PDF report generated: {filepath}") 