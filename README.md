# 🧠 NeuroCardioAI – Stroke Risk Prediction System

<p align="center">
  <strong>An AI-powered healthcare web application for demonstrating stroke-risk prediction using Machine Learning.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Machine%20Learning-Scikit--learn-orange" alt="Machine Learning">
  <img src="https://img.shields.io/badge/Database-SQLite-lightgrey?logo=sqlite" alt="SQLite">
  <img src="https://img.shields.io/badge/Status-Academic%20Project-blue" alt="Project Status">
</p>

---

## 📌 Project Overview

**NeuroCardioAI** is a machine-learning-based web application developed to demonstrate how artificial intelligence can be integrated into healthcare-oriented software.

The application provides a web interface where users can enter patient-related information, obtain a stroke-risk prediction from trained machine-learning models, and explore related healthcare analysis features.

The project combines a Python Flask backend, machine-learning components, database management, and interactive frontend technologies into a single application.

### 🎯 Project Objectives

- Demonstrate the practical application of machine learning in healthcare.
- Build an interactive web application using Flask.
- Integrate trained machine-learning models into a web application.
- Manage user information and prediction history.
- Present prediction-related information through reports and visualizations.
- Explore image-processing and 3D visualization concepts.

## ✨ Key Features

| Feature | Description |
|---|---|
| 👤 User Authentication | User registration and login functionality. |
| 🧠 Stroke Risk Prediction | Uses integrated machine-learning models to generate predictions from patient-related inputs. |
| 📊 Prediction History | Maintains prediction-related records for users. |
| 📄 Report Generation | Supports report generation for application results. |
| 🛡️ Admin Dashboard | Provides administrative application functionality. |
| 📧 Email Notifications | Includes email notification functionality using SMTP. |
| 📈 Data Visualization | Presents information through interactive visual components. |
| 🩻 MRI Upload | Supports MRI image uploads for demonstration purposes. |
| 🔬 Image Visualization | Includes demonstration image-processing and heatmap visualization components. |
| 🧊 3D Visualization | Includes 3D visualization elements for the application interface. |

## 🏗️ System Architecture

The application follows a layered web-application approach:

```text
          USER
            |
            v
     Frontend Interface
    (HTML, CSS, JavaScript)
            |
            v
       Flask Backend
            |
      +-----+------+
      |            |
      v            v
  Application   Machine Learning
    Logic          Models
      |            |
      +------+-----+
             |
             v
        Database
         (SQLite)
             |
             v
      Prediction Results
             |
       +-----+------+
       |            |
       v            v
    Dashboard    Reports
```

### 🔄 Application Workflow

1. The user accesses the web application.
2. The user registers or logs into the application.
3. The user enters the required information through the interface.
4. The Flask backend processes the submitted information.
5. The integrated machine-learning functionality generates a prediction.
6. The application displays the result.
7. Relevant application records and prediction history can be accessed through the interface.

## 🛠️ Technology Stack

| Category | Technologies | Purpose |
|---|---|---|
| Programming Language | Python | Backend development and ML integration |
| Backend Framework | Flask | Web application and request handling |
| Machine Learning | Scikit-learn | Machine-learning model integration |
| Deep Learning | TensorFlow, Keras | Neural-network model support |
| Image Processing | OpenCV | Image-processing functionality |
| Database | SQLite | Application data storage |
| ORM | SQLAlchemy | Database interaction |
| Frontend | HTML5, CSS3, JavaScript | User interface |
| Data Visualization | Chart.js | Interactive charts |
| 3D Visualization | Three.js | 3D interface components |
| Email Integration | SMTP | Email notifications |

## 📂 Project Structure

```text
AI_based_Stroke_risk_prediction/
│
├── api/                  # Application API modules
│
├── database/             # Database models and initialization
│
├── models/               # Machine-learning model artifacts
│
├── static/               # CSS, JavaScript, images and uploads
│
├── templates/            # HTML templates