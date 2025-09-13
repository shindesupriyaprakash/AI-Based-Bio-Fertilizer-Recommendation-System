from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd

app = Flask(__name__)

# Load model, scaler, and LabelEncoder
with open("rf_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("le.pkl", "rb") as f:
    le = pickle.load(f)

# Crop → Biofertilizer mapping
crop_to_biofert = {
    "rice": "Compost",
    "wheat": "Vermicompost",
    "maize": "Farmyard Manure",
    "millet": "Rhizobium",
    "barley": "Azospirillum",
    "sugarcane": "Farmyard Manure",
    "cotton": "Vermicompost",
    "pulses": "Rhizobium",
    "oilseeds": "Compost",
    "fruits": "Vermicompost",
    "vegetables": "Compost",
    "coffee": "Farmyard Manure",
    "tea": "Azospirillum"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    df = pd.DataFrame([data])
    
    # Feature engineering
    df["N_to_P"] = df["N"] / (df["P"] + 1)
    df["N_to_K"] = df["N"] / (df["K"] + 1)
    df["P_to_K"] = df["P"] / (df["K"] + 1)
    
    # Scale
    df_scaled = scaler.transform(df)
    
    # Predict crop
    crop_encoded = model.predict(df_scaled)[0]
    crop_pred = le.inverse_transform([crop_encoded])[0]
    
    # Predict bio-fertilizer
    bio_pred = crop_to_biofert.get(crop_pred, "Compost")
    dosage_dict = {
        "Compost": 200,
        "Vermicompost": 150,
        "Farmyard Manure": 180,
        "Rhizobium": 100,
        "Azospirillum": 120
    }
    dosage = dosage_dict.get(bio_pred, 150)
    
    return jsonify({"crop": crop_pred, "biofertilizer": bio_pred, "dosage": dosage})

if __name__ == "__main__":
    app.run(debug=True)
