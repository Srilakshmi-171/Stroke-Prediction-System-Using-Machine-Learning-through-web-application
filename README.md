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
│
├── utils/                # Helper functions and utilities
│
├── app.py                # Flask application setup
├── run.py                # Application startup script
├── config.py             # Application configuration
│
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
└── .gitignore             # Git ignored files
```

## 🚀 Installation and Setup

Follow these steps to run the project locally.

### Prerequisites

Make sure the following are installed:

- Python 3.x
- pip (Python package manager)
- Git
- A code editor such as VS Code or PyCharm

### 1. Clone the repository

```bash
git clone https://github.com/Srilakshmi-171/Stroke-Prediction-System-Using-Machine-Learning-through-web-application.git
```

### 2. Navigate to the project directory

```bash
cd Stroke-Prediction-System-Using-Machine-Learning-through-web-application
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
.venv\Scripts\activate
```

### 5. Install the required dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables

Create a local `.env` file using the example template:

```bash
copy .env.example .env
```

Generate a secure Flask secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Add the generated secret key and the required configuration values to your `.env` file.

Configure email credentials and an OpenAI API key only if you intend to use those integrations.

> 🔐 **Security Note:** Never upload your `.env` file, passwords, API keys, or other sensitive credentials to GitHub.

### 7. Run the application

Start the application using:

```bash
python run.py
```

The startup script:

- Creates the required application directories.
- Initializes the database.
- Starts the Flask development server.

### 8. Open the application

Once the server starts, open:

**http://127.0.0.1:5000**

To stop the application, press `Ctrl + C` in the terminal.

## 🤖 Machine Learning Integration

The project includes machine-learning model artifacts in the `models/` directory.

These artifacts are integrated into the application's prediction functionality.

The broader project explores machine-learning and deep-learning technologies for healthcare-oriented prediction and analysis.

**Model evaluation:** Actual performance metrics should be reported only after evaluating the models against an appropriate test dataset. No unverified accuracy claims are made in this documentation.

## 🩻 MRI Visualization – Implementation Note

The application includes an MRI upload and visualization demonstration.

The current implementation uses demonstration heatmap patterns and predefined findings. It does **not** currently perform validated MRI-based stroke detection or genuine Grad-CAM interpretation.

This functionality is included to demonstrate image-upload handling and visualization concepts, not to provide medical image analysis.

## 🔒 Security and Privacy Considerations

- Environment variables are used for sensitive configuration.
- Local databases and uploaded patient files are excluded from Git tracking.
- API keys and email credentials should remain private.
- Medical or personal information should not be uploaded to public repositories.
- Production deployment would require additional security, privacy, and access-control measures.

## 🔮 Future Enhancements

- Improve machine-learning model evaluation and validation.
- Add model-performance metrics and visual comparisons.
- Strengthen authentication and authorization.
- Expand automated testing.
- Implement validated medical image analysis.
- Improve API documentation.
- Add production deployment support.
- Enhance the user interface and reporting experience.

## ⚠️ Disclaimer

NeuroCardioAI is an academic and educational software project.

It is not a certified medical device. Its predictions, reports, and visualizations have not been clinically validated and must not be used for medical diagnosis, treatment, or clinical decision-making.

Always consult qualified healthcare professionals for medical advice.

## 👩‍💻 Author

**Srilakshmi**

- GitHub: [Srilakshmi-171](https://github.com/Srilakshmi-171)

## 🔗 Project Repository

[NeuroCardioAI – Stroke Risk Prediction System](https://github.com/Srilakshmi-171/Stroke-Prediction-System-Using-Machine-Learning-through-web-application)

---

<p align="center">
  <strong>Built with Python, Flask and Machine Learning.</strong>
  <br>
  <sub>Academic Project | Healthcare Technology | Artificial Intelligence</sub>
</p>