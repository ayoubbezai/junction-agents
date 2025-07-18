# main.py

from utils.data_loader import load_water_quality_data
from agents.water_quality_agent import WaterQualityAgent
from agents.mysql_gemmia_agent import MySQLGemmiaAgent
import google.generativeai as genai
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/sensor_reading"  # Change as needed
CSV_PATH = "data/waterquality.csv"


def run_iot_simulation():
    pond_id = input("Enter pond_id: ").strip()
    data = load_water_quality_data(CSV_PATH)
    agent = WaterQualityAgent(data, API_URL, pond_id=pond_id)
    agent.simulate_iot(period=2)


def send_to_gemini(prompt):
    # Set your Gemini API key
    genai.configure(api_key="AIzaSyCHlIBXW3UF7lUah8UtuP98-_MH_YU9nc4")
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    print("--- Gemini Response ---")
    print(response.text)
    print("--- End of Response ---")
    return response.text


def run_mysql_gemmia_report():
    agent = MySQLGemmiaAgent()  # Uses default DB and Gemmia key
    agent.connect_mysql()
    pond_id = input("Enter pond_id: ").strip()
    period = input("Enter period (e.g., 'week', 'month'): ").strip().lower()
    # Example: get last 7 or 30 days for the pond
    if period == 'week':
        query = f"SELECT * FROM sensor_readings WHERE pond_id = '{pond_id}' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) ORDER BY date DESC;"
    elif period == 'month':
        query = f"SELECT * FROM sensor_readings WHERE pond_id = '{pond_id}' AND created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH) ORDER BY date DESC;"
    else:
        query = f"SELECT * FROM sensor_readings WHERE pond_id = '{pond_id}' ORDER BY created_at DESC LIMIT 30;"
    data = agent.fetch_data(query)

    # Convert data to CSV for Gemini
    if data:
        df = pd.DataFrame(data)
        for col in df.columns:
            df[col] = df[col].astype(str)
        table_str = df.to_csv(index=False)
    else:
        table_str = "No data available."

    # Improved prompt for Gemini
    prompt = (
        "You are AQUAINTEL — a Real-Time Smart Aquaculture Assistant. "
        "You receive water quality sensor readings for a pond of fish. "
        "Each record contains: id, date, salinity, dissolved_oxygen, ph, secchi_depth, water_depth, water_temp, air_temp, created_at, updated_at, and pond_id. "
        f"Your task is to generate a comprehensive, professional report for pond_id {pond_id} for the last {period}. "
        "Analyze trends, highlight anomalies, and provide actionable recommendations for aquaculture management. "
        "Summarize the overall water quality, note any risks to fish health, and suggest improvements. "
        "Structure the report with an executive summary, key findings, and recommendations. "
        "If the dataset is small, still generate a summary and clearly mention to the user that the dataset is limited and results may not be fully representative. "
        "Here is the data in CSV format:\n" + table_str
    )
    print(table_str)
    print("--- Gemini Prompt ---")
    print(prompt)
    print("--- End of Prompt ---")
    # Send to Gemini and print the result
    summary = send_to_gemini(prompt)
    print(summary)

    # Remove generic Gemini intro if present
    lines = summary.splitlines()
    filtered_lines = []
    skip_phrases = [
        "Okay, I will generate a water quality report",
        "Okay, I will analyze the provided aquaculture data",
        "Due to the limited dataset, the analysis may not be fully representative",
        "Based on the provided sensor data",
        "Here is the report:",
        "Here is your report:",
        "Here is a report:",
        "Here is an analysis:",
        "Here is the analysis:",
    ]
    for line in lines:
        if not any(phrase.lower() in line.lower() for phrase in skip_phrases):
            filtered_lines.append(line)
    cleaned_summary = "\n".join(filtered_lines).strip()

    # Generate a styled PDF report with only the cleaned summary
    pdf_data = [cleaned_summary]
    agent.generate_pdf_report(pdf_data)


def main():
    print("Select agent to run:")
    print("1. IoT Water Quality Simulator")
    print("2. MySQL & Gemmia PDF Report Generator")
    choice = input("Enter 1 or 2: ").strip()
    if choice == "1":
        run_iot_simulation()
    elif choice == "2":
        run_mysql_gemmia_report()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main() 