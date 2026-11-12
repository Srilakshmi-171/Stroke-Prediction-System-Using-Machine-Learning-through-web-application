from app import app, db
from utils.email_service import send_welcome_email
from database.models import User

with app.app_context():
    # Get first user
    user = User.query.first()
    if user:
        print(f"Sending test email to {user.email}")
        success = send_welcome_email(user)
        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Failed to send email")
    else:
        print("No users found")