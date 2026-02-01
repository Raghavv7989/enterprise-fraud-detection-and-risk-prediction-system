import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib, os

df = pd.read_csv("data/transactions.csv")
X = df.drop("fraud", axis=1)
y = df["fraud"]

model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42
)
model.fit(X, y)

os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/fraud_model.pkl")