# agents/water_quality_agent.py

import time
import requests
from datetime import datetime

class WaterQualityAgent:
    def __init__(self, data, api_url, pond_id=None):
        self.data = data
        self.api_url = api_url
        self.pond_id = pond_id

    def row_to_payload(self, row):
        # Format date as 'YYYY-MM-DD HH:MM:SS'
        date_str = row[0]
        try:
            # Try parsing as date only
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_formatted = date_obj.strftime("%Y-%m-%d 00:00:00")
        except Exception:
            date_formatted = date_str  # fallback
        payload = {
            "date": date_formatted,
            "salinity": self._to_float(row[1]),
            "dissolved_oxygen": self._to_float(row[2]),
            "ph": self._to_float(row[3]),
            "secchi_depth": self._to_float(row[4]),
            "water_depth": self._to_float(row[5]),
            "water_temp": self._to_float(row[6]),
            "air_temp": self._to_float(row[7]),
        }
        if self.pond_id is not None:
            payload["pond_id"] = self.pond_id
        return payload

    def _to_float(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def simulate_iot(self, period=5):
        # Skip header
        for i, row in enumerate(self.data[1:]):
            payload = self.row_to_payload(row)
            try:
                response = requests.post(self.api_url, json=payload)
                print(f"[{i+1}] Sent: {payload} | Status: {response.status_code}")
            except Exception as e:
                print(f"[{i+1}] Error sending data: {e}")
            time.sleep(period) 