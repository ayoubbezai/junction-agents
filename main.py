# main.py

from utils.data_loader import load_water_quality_data
from agents.water_quality_agent import WaterQualityAgent
from agents.mysql_gemmia_agent import MySQLGemmiaAgent
from agents.gemini_task_agent import GeminiTaskAgent
from agents.model_predictor import AquaIntelPredictor
import google.generativeai as genai
import pandas as pd
import joblib
import os

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


def run_gemini_task_agent():
    agent = GeminiTaskAgent()
    pond_id = input("Enter pond_id: ").strip()
    print("Using sample data for Gemini Task Agent...")
    user_input = '''"data": { "current_page": 1, "total_pages": 1, "total_items": 2, "per_page": 15, "items": [ { "id": 1, "location": "North Zone", "pond_name": "Pond Alpha", "size": "Large", "safe_range": { "ph": { "min": 7, "max": 12, "unit": "pH" }, "temperature": { "min": 20, "max": 30, "unit": "C" }, "oxygen": { "min": 5, "max": 10, "unit": "mg/L" } }, "region_id": 1, "created_at": "2025-07-18T01:49:09.000000Z", "updated_at": "2025-07-18T01:49:09.000000Z", "region": { "id": 1, "region_name": "batna", "created_at": "2025-07-18T01:49:06.000000Z", "updated_at": "2025-07-18T01:49:06.000000Z" } }, { "id": 2, "location": "North Zone", "pond_name": "Pond Alpha", "size": "Large", "safe_range": { "ph": { "min": 7, "max": 12, "unit": "pH" }, "temperature": { "min": 20, "max": 30, "unit": "C" }, "oxygen": { "min": 5, "max": 10, "unit": "mg/L" } }, "region_id": 1, "created_at": "2025-07-18T02:30:29.000000Z", "updated_at": "2025-07-18T02:30:29.000000Z", "region": { "id": 1, "region_name": "batna", "created_at": "2025-07-18T01:49:06.000000Z", "updated_at": "2025-07-18T01:49:06.000000Z" } } ] }\nFull texts\nid\ndate\nsalinity\ndissolved_oxygen\nph\nsecchi_depth\nwater_depth\nwater_temp\nair_temp\npond_id\ncreated_at\nupdated_at\n... (sensor data rows) ...\n🐟 Prediction Result:\nEnvironment Quality: Moderate\nBacteria Level: Low\n\n📌 Explanation:\n\n🔴 Dissolved oxygen is below optimal level (< 5 mg/L).\n⚠️ pH is outside the healthy range for fish (6.5–8.5).\n⚠️ Water transparency is low, which can affect light penetration.\n⚠️ Environment quality is moderate; it's not critical but requires monitoring.\n'''
    print("\nGenerating tasks with Gemini AI...")
    tasks = agent.generate_tasks(user_input)
    print("\n--- Gemini AI Task List ---")
    print(tasks)
    print("--- End of Task List ---\n")
    # Send tips to API
    status, resp = agent.send_tips_to_api(pond_id, tasks)
    print(f"Sent to API (status {status}): {resp}")


def run_model_prediction():
    predictor = AquaIntelPredictor()
    # Hardcoded example input for tomorrow's prediction
    input_data = {
        "Month": 7,
        "DayOfYear": 199,        # July 17
        "Week": 29,
        "pH_lag1": 7.2,
        "pH_lag2": 7.1,
        "Turbidity_lag1": 2.8,
        "Turbidity_lag2": 2.9,
        "Conductivity_lag1": 300,
        "Conductivity_lag2": 310,
        "DissolvedOxygen_lag1": 8.5,
        "DissolvedOxygen_lag2": 8.3,
        "BOD_lag1": 2.1,
        "BOD_lag2": 2.2,
        "Nitrate_lag1": 0.5,
        "Nitrate_lag2": 0.6,
        "TotalColiform_lag1": 12,
        "TotalColiform_lag2": 10
    }
    prediction = predictor.predict(input_data)
    print("Prediction for tomorrow:")
    for target, value in prediction.items():
        print(f"{target}: {value:.2f}")


def main():
    print("Select agent to run:")
    print("1. IoT Water Quality Simulator")
    print("2. MySQL & Gemmia PDF Report Generator")
    print("3. Gemini Task Generator (AI-powered TODOs)")
    print("4. Run ML Prediction")
    choice = input("Enter 1, 2, 3, or 4: ").strip()
    if choice == "1":
        run_iot_simulation()
    elif choice == "2":
        run_mysql_gemmia_report()
    elif choice == "3":
        run_gemini_task_agent()
    elif choice == "4":
        run_model_prediction()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main() 