# It is Universal OTP Decorator used for all api's
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from Db_connections.configurations import session
from Logging_package.logging_utility import log_error, log_info
from User_models.tables import OTPStore


def otp_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        payload = request.get_json()
        email = None
        try:
            if not payload or 'email' not in payload or 'otp' not in payload:
                log_error("OTP validation failed: Email and OTP are required.")
                return jsonify({"error": "Email and OTP are required."}), 400

            email = payload['email']
            otp = payload['otp']

            otp_record = session.query(OTPStore).filter_by(email=email).order_by(OTPStore.timestamp.desc()).first()

            if not otp_record:
                log_error(f"OTP validation failed: No OTP generated for {email}.")
                return jsonify({"error": "No OTP generated for this email."}), 400

            # Check if OTP is expired (valid for 5 minutes)
            if datetime.now() - otp_record.timestamp > timedelta(minutes=60):
                log_error(f"OTP validation failed: OTP for {email} has expired.")
                return jsonify({"error": "OTP has expired."}), 400

            if otp != otp_record.otp:
                log_error(f"OTP validation failed: Invalid OTP for {email}.")
                return jsonify({"error": "Invalid OTP."}), 400

            log_info(f"OTP validation successful for {email}.")
            return func(*args, **kwargs)

        except SQLAlchemyError as db_error:
            session.rollback()
            log_error(f"Database error while validating OTP for {email}: {db_error}")
            return jsonify({"error": "Internal server error", "details": str(db_error)}), 500

        except Exception as e:
            log_error(f"Unexpected error while validating OTP for {email}: {e}")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500

        finally:
            session.close()

    return wrapper


def validate_email(email):
    """
    Validates the email format.

    :param email: (str) Email address to validate.
    :return: (bool) True if valid, False otherwise.
    """
    import re
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email) is not None