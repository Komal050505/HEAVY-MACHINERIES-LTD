import psycopg2
import random
from datetime import datetime

from flask import request, jsonify, Flask
from sqlalchemy.exc import SQLAlchemyError

from Db_connections.configurations import session
from Logging_package.logging_utility import log_error, log_info
from User_models.tables import OTPStore
from email_setup.email_operations import send_email_otp

app = Flask(__name__)


@app.route('/generate-otp', methods=['POST'])
def generate_otp():
    """
    Generates a One-Time Password (OTP) for the given email and sends it via email.
    The OTP is stored in the database for verification purposes.

    :return: JSON response indicating success or error.
    """
    email = None
    try:
        payload = request.get_json()
        if not payload or 'email' not in payload:
            log_error("Email is required to generate OTP.")
            return jsonify({"error": "Email is required to generate OTP."}), 400

        email = payload['email']
        otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
        timestamp = datetime.now()

        new_otp = OTPStore(email=email, otp=otp, timestamp=timestamp)
        session.add(new_otp)
        session.commit()

        log_info(f"Generated OTP for {email}: {otp}")

        send_email_otp(email, otp)

        return jsonify({"message": f"OTP sent to {email}",
                        "otp": f"OTP is {otp}"}), 200

    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Database error occurred while generating OTP for {email}: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        session.rollback()
        log_error(f"Unexpected error occurred while generating OTP for {email}: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    finally:
        session.close()
        log_info(f"End of generate_otp function for email={email}")


if __name__ == "__main__":
    log_info(f"Starting the Flask application {app}.")
    app.run(debug=True)
    log_info("Flask application has stopped.")
