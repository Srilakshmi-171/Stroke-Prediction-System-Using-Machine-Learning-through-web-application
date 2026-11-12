import os
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# ==============================
# CREATE MODELS FOLDER
# ==============================
os.makedirs("models", exist_ok=True)

# ==============================
# LOAD DATASET
# ==============================
data = pd.read_csv("stroke_dataset.csv")

print("Dataset shape:", data.shape)

# ==============================
# HANDLE MISSING VALUES
# ==============================

y = data["stroke"]
X = data.drop(columns=["stroke"], errors="ignore")

num_cols = X.select_dtypes(include=["int64", "float64"]).columns
cat_cols = X.select_dtypes(include=["object"]).columns

# Impute numeric
num_imputer = SimpleImputer(strategy="mean")
X[num_cols] = num_imputer.fit_transform(X[num_cols])

# Impute categorical
cat_imputer = SimpleImputer(strategy="most_frequent")
X[cat_cols] = cat_imputer.fit_transform(X[cat_cols])

# ==============================
# ENCODE CATEGORICAL FEATURES
# ==============================

encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le

pickle.dump(encoders, open("models/encoder.pkl", "wb"))

# ==============================
# SCALE FEATURES
# ==============================

scaler = StandardScaler()
X[num_cols] = scaler.fit_transform(X[num_cols])

pickle.dump(scaler, open("models/scaler.pkl", "wb"))

X = X.values
y = y.values

# ==============================
# TRAIN TEST SPLIT
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ==============================
# BUILD ANN MODEL
# ==============================

model = Sequential([
    Dense(128, activation='relu', input_shape=(X.shape[1],)),
    Dropout(0.4),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Early stopping to prevent overfitting
early_stop = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

# ==============================
# TRAIN MODEL
# ==============================

history = model.fit(
    X_train,
    y_train,
    epochs=50,
    batch_size=16,
    validation_split=0.2,
    callbacks=[early_stop],
    verbose=1
)

# ==============================
# EVALUATE MODEL
# ==============================

loss, accuracy = model.evaluate(X_test, y_test)
print("ANN Test Accuracy:", round(accuracy, 4))

# ==============================
# SAVE MODELS
# ==============================

model.save("models/brain_ann.h5")
model.save("models/heart_ann.h5")

print("ANN models trained and saved successfully.")