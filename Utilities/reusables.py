# It is Universal OTP Decorator used for all api's
import re
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
            if datetime.now() - otp_record.timestamp > timedelta(minutes=3600):
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


def get_opportunity_stage(probability):
    """
    Determine the sales opportunity stage based on the probability value.

    :param probability: Integer representing the probability percentage (0 to 100).
    :return: String representing the stage name.
    :raises ValueError: If the probability value is out of range (0-100) or invalid.
    """
    if 10 <= probability <= 20:
        return "Prospecting"
    elif 21 <= probability <= 40:
        return "Qualification"
    elif 41 <= probability <= 60:
        return "Needs Analysis"
    elif 61 <= probability <= 70:
        return "Value Proposition"
    elif 71 <= probability <= 80:
        return "Decision Makers"
    elif 81 <= probability <= 85:
        return "Perception Analysis"
    elif 86 <= probability <= 90:
        return "Proposal/Price Quote"
    elif 91 <= probability <= 95:
        return "Negotiation/Review"
    elif probability == 100:
        return "Closed Won"
    elif probability == 0:
        return "Closed Lost"
    else:
        raise ValueError("Invalid probability value")


def get_currency_conversion(amount):
    """
    Convert a given amount from INR to various other currencies using predefined rates.

    :param amount: Amount in INR to be converted.
    :return: Dictionary with the amount converted to various currencies (USD, AUD, CAD, JPY, EUR, GBP, CNY) and INR.
    """
    # Dummy conversion rates (assumed for demonstration)
    usd_rate = 10
    aus_rate = 5
    cad_rate = 1
    jpy_rate = 1.76
    eur_rate = 0.012
    gbp_rate = 20
    cny_rate = 6

    # Perform currency conversions
    usd = amount * usd_rate
    aus = amount * aus_rate
    cad = amount * cad_rate
    jpy = amount * jpy_rate
    eur = amount * eur_rate
    gbp = amount * gbp_rate
    cny = amount * cny_rate

    # Return a dictionary with all conversions rounded to 2 decimal places
    return {
        'USD': round(usd, 2),
        'AUD': round(aus, 2),
        'CAD': round(cad, 2),
        'JPY': round(jpy, 2),
        'EUR': round(eur, 2),
        'GBP': round(gbp, 2),
        'CNY': round(cny, 2),
        'INR': round(amount, 2)  # Original amount in INR
    }


def validate_probability(prob):
    """
    Validate probability value.
    :param prob: Probability value.
    :return: Boolean indicating validity.
    """
    return isinstance(prob, int) and 0 <= prob <= 100


def validate_positive_number(value):
    """
    Validate positive number.
    :param value: Number to validate.
    :return: Boolean indicating validity.
    """
    return isinstance(value, (int, float)) and value > 0


def validate_stage(stage_str):
    """
    Validate stage value.
    :param stage_str: Stage value to validate.
    :return: None if valid, otherwise raises ValueError.
    """
    stage_str = stage_str.strip()  # Remove leading and trailing spaces
    if not stage_str:
        raise ValueError("Stage value cannot be empty or contain only spaces.")
    if not re.match(r'^[A-Za-z\s]+$', stage_str):
        raise ValueError(f"Invalid stage value: '{stage_str}'. Must contain only letters and spaces.")
    if len(stage_str) > 100:  # Assuming a max length of 100 characters
        raise ValueError(f"Stage is too long. Maximum length is 100 characters.")
    return stage_str
