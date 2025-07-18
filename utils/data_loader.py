# utils/data_loader.py

import csv

def load_water_quality_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data 