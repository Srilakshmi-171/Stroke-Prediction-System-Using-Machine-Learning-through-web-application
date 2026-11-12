import os
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
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

num_imputer = SimpleImputer(strategy="mean")
X[num_cols] = num_imputer.fit_transform(X[num_cols])

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
# DYNAMIC RESHAPING FOR CNN
# ==============================
num_features = X.shape[1]

# Make square-like shape automatically
height = int(np.sqrt(num_features))
width = int(np.ceil(num_features / height))

# Pad if needed
padding_needed = height * width - num_features
if padding_needed > 0:
    X = np.pad(X, ((0, 0), (0, padding_needed)), mode='constant')

X = X.reshape(-1, height, width, 1)

print("CNN Input Shape:", X.shape)

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
# BUILD CNN MODEL
# ==============================
model = Sequential([
    Conv2D(32, (2,2), activation='relu', input_shape=(height, width, 1)),
    MaxPooling2D((1,1)),
    Conv2D(64, (2,2), activation='relu'),
    Flatten(),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

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
    epochs=30,
    batch_size=16,
    validation_split=0.2,
    callbacks=[early_stop],
    verbose=1
)

# ==============================
# EVALUATE MODEL
# ==============================
loss, accuracy = model.evaluate(X_test, y_test)
print("CNN Test Accuracy:", round(accuracy, 4))

# ==============================
# SAVE MODELS
# ==============================
model.save("models/brain_cnn.h5")
model.save("models/heart_cnn.h5")

print("Tabular CNN models trained and saved successfully.")