\# NeuroCardioAI – Stroke Risk Prediction System



An educational web application that combines machine learning and web technologies to demonstrate stroke-risk prediction and related healthcare features.



\## Overview



NeuroCardioAI is a Flask-based web application designed to demonstrate how machine learning can be integrated into a healthcare-oriented application. It provides a web interface for entering patient information, viewing prediction results, and exploring related analysis features.



\*\*Important:\*\* This project is for educational and demonstration purposes only. Its predictions and visualizations are not clinically validated and must not be used for medical diagnosis or treatment decisions.



\## Features



\- User registration and authentication

\- Stroke-risk prediction using machine learning

\- Prediction history and report generation

\- Admin dashboard

\- Email notification functionality

\- Data visualization and analysis

\- MRI upload and demonstration visualization

\- 3D visualization components



\*\*MRI visualization note:\*\* The current MRI visualization implementation is a demonstration feature. It does not perform validated medical image analysis or genuine Grad-CAM-based interpretation.



\## Technology Stack



| Area | Technologies |

|---|---|

| Backend | Python, Flask |

| Machine Learning | Scikit-learn, TensorFlow, Keras |

| Image Processing | OpenCV |

| Database | SQLite, SQLAlchemy |

| Frontend | HTML, CSS, JavaScript |

| Visualization | Chart.js, Three.js |

| Email | SMTP |



\## Project Structure



```text

AI\_based\_Stroke\_risk\_prediction/

│

├── api/

├── database/

├── models/

├── static/

├── templates/

├── utils/

├── app.py

├── run.py

├── config.py

├── requirements.txt

├── .env.example

└── .gitignore

```



\## Getting Started



\### 1. Clone the repository



```bash

git clone https://github.com/Srilakshmi-171/Stroke-Prediction-System-Using-Machine-Learning-through-web-application.git

```



\### 2. Navigate to the project directory



```bash

cd Stroke-Prediction-System-Using-Machine-Learning-through-web-application

```



\### 3. Create a virtual environment



```bash

python -m venv .venv

```



\### 4. Activate the virtual environment



Windows:



```bash

.venv\\Scripts\\activate

```



\### 5. Install dependencies



```bash

pip install -r requirements.txt

```



\### 6. Configure environment variables



Create your local environment file:



```bash

copy .env.example .env

```



Generate a secure Flask secret key:



```bash

python -c "import secrets; print(secrets.token\_hex(32))"

```



Add the generated value and your required configuration details to `.env`.



Configure email credentials and an OpenAI API key only if you intend to use those integrations.



\*\*Security:\*\* Never commit `.env`, passwords, API keys, or other private credentials to GitHub.



\### 7. Start the application



```bash

python run.py

```



The startup script creates required directories, initializes the database, and starts the Flask development server.



Open your browser:



```text

http://127.0.0.1:5000

```



Press `Ctrl + C` in the terminal to stop the server.



\## Machine Learning Models



The project includes trained model files used by its prediction functionality. These files are stored in the `models/` directory.



The repository includes model artifacts, but the quality and clinical validity of predictions have not been independently established.



\## Future Improvements



\- Improve model evaluation and validation

\- Add stronger security and access-control measures

\- Improve automated testing

\- Develop validated medical image analysis capabilities

\- Add production deployment configuration

\- Improve documentation and API testing



\## Disclaimer



This application is an academic and educational project. It is not a medical device and is not intended to replace professional medical advice, diagnosis, or treatment.



\## Author



\*\*Srilakshmi\*\*



GitHub: \[Srilakshmi-171](https://github.com/Srilakshmi-171)



Project Repository: \[NeuroCardioAI – Stroke Risk Prediction System](https://github.com/Srilakshmi-171/Stroke-Prediction-System-Using-Machine-Learning-through-web-application)

