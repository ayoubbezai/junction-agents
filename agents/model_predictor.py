import joblib
import pandas as pd
import os

class AquaIntelPredictor:
    def __init__(self, model_path=None, scaler_path=None, features_path=None):
        base_dir = os.path.dirname(__file__)
        if model_path is None:
            model_path = os.path.join(base_dir, '..', 'models', 'water_model.pkl')
        if scaler_path is None:
            scaler_path = os.path.join(base_dir, '..', 'models', 'scaler.pkl')
        if features_path is None:
            features_path = os.path.join(base_dir, '..', 'models', 'input_features.pkl')

        # Load trained objects
        self.models = joblib.load(model_path)       # Dictionary of models
        self.scaler = joblib.load(scaler_path)      # MinMaxScaler
        self.expected_features = joblib.load(features_path)  # List of feature names used during training

    def predict(self, input_data):
        # Ensure input is a DataFrame
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])
        elif isinstance(input_data, pd.Series):
            input_data = input_data.to_frame().T

        # Reorder and filter columns to match training features
        input_data = input_data.reindex(columns=self.expected_features, fill_value=0)

        # Scale
        input_scaled = self.scaler.transform(input_data)

        # Predict for each target variable
        results = {}
        for target, model in self.models.items():
            results[target] = model.predict(input_scaled)[0]

        return results
