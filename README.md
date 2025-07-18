# AQUAINTEL — Real-Time Smart Aquaculture Assistant

AQUAINTEL is a Python-based system for real-time water quality monitoring, actionable task generation, and professional reporting in aquaculture environments. It features:

- **IoT Simulation Agent**: Sends water quality sensor data from CSV to an API, simulating real-time IoT device behavior.
- **MySQL & Gemini AI Reporting Agent**: Fetches pond sensor data from MySQL, summarizes it using Google Gemini AI, and generates a branded, professional PDF report.
- **Gemini Task Generator Agent**: Accepts pond data, sensor readings, and prediction results, then uses Gemini AI to generate concise, actionable tips and tasks for farmers. Tips are sent to your backend API for real-time guidance.

## Features

- **IoT Simulation**: Periodically sends each row of water quality data to a specified API endpoint, including a user-supplied `pond_id`.
- **AI-Powered Reporting**: Generates actionable, executive-level reports for any pond and period (week/month/custom) using Gemini AI, with clear findings and recommendations.
- **Task Generation & Alerting**: Instantly generates short, actionable tips for farmers based on live or predicted pond data and sends them to your backend API.
- **Professional PDF Output**: Each report includes your logo, a title, Gemini AI summary, and a timestamped footer. Reports are saved in the `pdf/` folder with unique filenames.

## Project Structure

```
junction agents/
│
├── app.py                # (Legacy entry point)
├── main.py               # Main entry point for all agents
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
│
├── data/                 # Contains waterquality.csv and other datasets
├── pdf/                  # All generated PDF reports
├── assets/               # Contains fishtaLogo.png (logo for reports)
├── agents/               # Agent logic (IoT, MySQL/Gemini, Task)
└── utils/                # Utility functions (e.g., data loading)
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure your MySQL database** (see `agents/mysql_gemmia_agent.py` for default credentials or set environment variables).
3. **Place your logo** in `assets/fishtaLogo.png` (PNG recommended).
4. **(Optional) Update API endpoints** in `main.py` as needed.

## Usage

Run the main program:
```bash
python main.py
```
You will be prompted to select:
- **1. IoT Water Quality Simulator**: Enter a `pond_id` to simulate sending sensor data to your API.
- **2. MySQL & Gemini PDF Report Generator**: Enter a `pond_id` and period (`week`, `month`, or custom) to generate a professional PDF report for that pond.
- **3. Gemini Task Generator (AI-powered TODOs & Tips)**: Enter a `pond_id` and the agent will use sample or live data to generate concise, actionable tips for the farmer. These tips are sent as JSON to your backend API (`/api/tips`).

## PDF Report Features
- **Logo and Branding**: Your logo appears at the top of every report.
- **Title and Gemini AI Subtitle**: Clearly labeled as an AQUAINTEL Gemini AI report.
- **Executive Summary**: AI-generated, actionable summary of water quality trends, risks, and recommendations.
- **Footer**: Timestamp of report generation.
- **Automatic File Management**: All reports are saved in `pdf/` with unique names.

## Task Generator Features
- **Short, Actionable Tips**: Each tip is 1-2 lines for fast action.
- **Context-Aware**: Tips are based on pond details, safe ranges, sensor data, and prediction results.
- **Automatic API Integration**: Tips are sent as JSON to your backend for real-time farmer guidance.

## Requirements
- Python 3.8+
- See `requirements.txt` for all dependencies (includes `fpdf`, `pandas`, `google-generativeai`, etc.)

## Customization
- Update the logo in `assets/` for your own branding.
- Adjust the report and task prompts in `main.py` or agent files for different summary or tip styles.
- Change the API endpoint or database credentials as needed.

---

For questions or further customization, contact the project maintainer.