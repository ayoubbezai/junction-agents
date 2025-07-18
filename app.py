# app.py

from utils.data_loader import load_water_quality_data
from agents.water_quality_agent import WaterQualityAgent

API_URL = "http://127.0.0.1:8000/api/sensor_reading" 

if __name__ == "__main__":
    data = load_water_quality_data("data/waterquality.csv")
    agent = WaterQualityAgent(data, API_URL)
    agent.simulate_iot(period=5)
