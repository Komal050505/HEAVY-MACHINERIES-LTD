from datetime import datetime

from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError

from App.constants import REQUIRED_FIELDS_FOR_CUSTOMER_CREATION
from Db_connections.configurations import session
from Logging_package.logging_utility import log_info, log_warning, log_error
from User_models.tables import HeavyMachineryCustomer
from Utilities.reusables import otp_required
from email_setup.email_config import RECEIVER_EMAIL
from email_setup.email_operations import send_email, generate_customer_email_body

app = Flask(__name__)


@app.route('/add-customer', methods=['POST'])
@otp_required
def add_customer():
    """
    Add a new heavy machinery customer to the database.

    This endpoint receives a JSON object containing customer details,
    validates the input, and adds a new customer record if all validations pass.

    :return: JSON response with a success message and customer details if successful.
    """
    log_info(f"Entered /add-customer endpoint. Request method: {request.method}")

    try:
        data = request.get_json()
        log_info(f"Received request data: {data}")

        for field in REQUIRED_FIELDS_FOR_CUSTOMER_CREATION:
            if field not in data:
                log_warning(f"Missing field: {field} in request data")
                return jsonify({"message": f"Missing field: {field}"}), 400

        new_customer = HeavyMachineryCustomer(
            customer_name=data['customer_name'],
            customer_contact_info=data['customer_contact_info'],
            customer_address=data['customer_address'],
            opportunity_id=data.get('opportunity_id'),
            dealer_id=data.get('dealer_id'),
            employee_id=data.get('employee_id'),
            customer_status=data.get('customer_status', 'new'),
            customer_comments=data.get('customer_comments'),
            customer_feedback=data.get('customer_feedback'),
            customer_last_interaction=datetime.utcnow() if 'customer_last_interaction' in data else None
        )

        log_info(f"New customer created: {new_customer.customer_name} - Ready for database insertion")

        session.add(new_customer)
        session.commit()
        log_info(f"Customer {new_customer.customer_name} added successfully to the database")

        email_body = generate_customer_email_body(new_customer)
        send_email(
            too_email=RECEIVER_EMAIL,
            subject="Welcome to Heavy Machinery Ltd",
            body=email_body
        )
        return jsonify({"message": "Customer added successfully!", "customer": new_customer.to_dict()}), 201

    except IntegrityError as e:
        session.rollback()
        log_error(f"Database Integrity Error: {str(e)}")
        return jsonify({"message": "An error occurred while adding the customer."}), 409
    except Exception as e:
        session.rollback()
        log_error(f"General Error adding customer: {str(e)}")
        return jsonify({"message": f"Error adding customer: {str(e)}"}), 500
    finally:
        session.close()
        log_info("Session closed for add-customer API")


if __name__ == "__main__":
    log_info(f"Starting the Flask application {app}.")
    app.run(debug=True)
    log_info("Flask application has stopped.")
