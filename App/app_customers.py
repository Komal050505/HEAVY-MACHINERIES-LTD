from datetime import datetime

from flask import Flask, request, jsonify
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from App.constants import REQUIRED_FIELDS_FOR_CUSTOMER_CREATION
from Db_connections.configurations import session
from Logging_package.logging_utility import log_info, log_warning, log_error, log_debug
from User_models.tables import HeavyMachineryCustomer, Employee
from Utilities.reusables import otp_required
from email_setup.email_config import RECEIVER_EMAIL
from email_setup.email_operations import send_email, generate_customer_email_body, generate_customers_email_body, \
    format_update_customers_email_content, send_customer_deletion_email

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
            customer_last_interaction=datetime.utcnow() if 'customer_last_interaction' in data else None,
            product_id=data.get('product_id'),
            product_name=data.get('product_name'),
            product_model=data.get('product_model'),
            product_brand=data.get('product_brand')
        )

        log_info(f"New customer created: {new_customer.customer_name} - Ready for database insertion")

        session.add(new_customer)
        session.commit()
        log_info(f"Customer {new_customer.customer_name} added successfully to the database")

        email_body = generate_customer_email_body(new_customer)
        send_email(
            too_email=RECEIVER_EMAIL,
            subject="New Customer Notification",
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


@app.route('/get-customers', methods=['GET'])
def get_customers():
    """
    Fetch single or multiple heavy machinery customers from the database.

    This endpoint receives optional query parameters for filtering customers
    by various attributes, including a specific customer ID.

    :return: JSON response with customer details or error message.
    """
    log_info(f"Entered /get-customers endpoint. Request method: {request.method}")

    try:
        customer_id = request.args.get('customer_id', '').strip()
        customer_name = request.args.get('customer_name', '').strip().lower()
        customer_contact_info = request.args.get('customer_contact_info', '').strip().lower()
        customer_address = request.args.get('customer_address', '').strip().lower()

        log_info(f"Received parameters - customer_id: {customer_id}, customer_name: {customer_name}, "
                 f"customer_contact_info: {customer_contact_info}, customer_address: {customer_address}")

        query = session.query(HeavyMachineryCustomer)

        if customer_id:
            log_info(f"Filtering by customer_id: {customer_id}")
            query = query.filter(HeavyMachineryCustomer.customer_id == customer_id)
        else:
            if customer_name:
                log_info(f"Filtering by customer_name: {customer_name}")
                query = query.filter(func.lower(HeavyMachineryCustomer.customer_name).like(f'%{customer_name}%'))
            if customer_contact_info:
                log_info(f"Filtering by customer_contact_info: {customer_contact_info}")
                query = query.filter(
                    func.lower(HeavyMachineryCustomer.customer_contact_info).like(f'%{customer_contact_info}%'))
            if customer_address:
                log_info(f"Filtering by customer_address: {customer_address}")
                query = query.filter(func.lower(HeavyMachineryCustomer.customer_address).like(f'%{customer_address}%'))

        log_info("Executing the query to fetch customers...")
        customers = query.all()
        customer_count = len(customers)
        log_info(f"Fetched {customer_count} customers based on filters")

        customer_list = [customer.to_dict() for customer in customers]
        log_info(f"Prepared customer list for response: {customer_list}")

        if customer_list:
            log_info("Preparing to send notification email with fetched customer details...")
            email_body = generate_customers_email_body(customer_list,
                                                       customer_count)
            send_email(
                too_email=RECEIVER_EMAIL,
                subject="Customer Fetch Notification",
                body=email_body
            )
            log_info("Notification email sent successfully.")

        return jsonify({
            "message": "Customers fetched successfully!",
            "customer_count": customer_count,
            "customers": customer_list
        }), 200

    except Exception as e:
        log_error(f"General Error fetching customers: {str(e)}")
        return jsonify({"message": f"Error fetching customers: {str(e)}"}), 500
    finally:
        session.close()
        log_info("Session closed for get-customers API")


@app.route('/update-customer', methods=['PUT'])
@otp_required
def update_customer():
    """
    Update customer details by customer ID.

    This endpoint updates all fields of a customer except for the customer ID,
    including product-related information.

    Request Body Parameters:
    customer_id (required)
    customer_name (optional)
    customer_contact_info (optional)
    customer_address (optional)
    opportunity_id (optional)
    dealer_id (optional)
    employee_id (optional)
    customer_status (optional)
    customer_comments (optional)
    customer_feedback (optional)
    customer_last_interaction (optional)
    product_id (optional)
    product_name (optional)
    product_brand (optional)
    product_model (optional)

    :return: JSON response with the updated customer details.
    """
    log_info("Entered /update-customer endpoint.")

    customer_id = None
    try:
        data = request.json
        log_debug(f"Request body received: {data}")

        customer_id = data.get('customer_id')
        if not customer_id:
            log_warning("Customer ID not provided in the request.")
            return jsonify({"message": "Customer ID is required."}), 400

        log_info(f"Fetching customer with ID: {customer_id}")
        customer = session.query(HeavyMachineryCustomer).filter_by(customer_id=customer_id).first()

        if not customer:
            log_warning(f"Customer with ID {customer_id} not found.")
            return jsonify({"message": f"Customer with ID {customer_id} not found."}), 404

        log_info(f"Current customer details: {customer.to_dict()}")

        customer.customer_name = data.get('customer_name', customer.customer_name)
        customer.customer_contact_info = data.get('customer_contact_info', customer.customer_contact_info)
        customer.customer_address = data.get('customer_address', customer.customer_address)
        customer.opportunity_id = data.get('opportunity_id', customer.opportunity_id)
        customer.dealer_id = data.get('dealer_id', customer.dealer_id)
        customer.employee_id = data.get('employee_id', customer.employee_id)
        customer.customer_status = data.get('customer_status', customer.customer_status)
        customer.customer_comments = data.get('customer_comments', customer.customer_comments)
        customer.customer_feedback = data.get('customer_feedback', customer.customer_feedback)
        customer.customer_last_interaction = data.get('customer_last_interaction', customer.customer_last_interaction)

        customer.product_id = data.get('product_id', customer.product_id)
        customer.product_name = data.get('product_name', customer.product_name)
        customer.product_brand = data.get('product_brand', customer.product_brand)
        customer.product_model = data.get('product_model', customer.product_model)

        log_info(f"Updated customer details (before commit): {customer.to_dict()}")

        session.commit()
        log_info(f"Customer with ID {customer_id} updated successfully in the database.")

        updated_customer = customer.to_dict()
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_info(f"Customer ID {customer_id} updated at {update_time}.")

        employee = session.query(Employee).filter_by(employee_id=data.get('emp_id')).first() if data.get(
            'emp_id') else None

        email_body = format_update_customers_email_content([updated_customer], update_time, employee)
        send_email(RECEIVER_EMAIL, f"Customer {customer_id} Updated", email_body)
        log_info(f"Email notification sent for customer ID {customer_id} update.")

        return jsonify({
            "message": "Customer updated successfully.",
            "updated_customer": updated_customer
        }), 200

    except Exception as e:
        session.rollback()
        log_error(f"Error updating customer ID {customer_id}: {str(e)}")
        return jsonify({"message": f"Error updating customer: {str(e)}"}), 500

    finally:
        session.close()
        log_info("Closed /update-customer API session.")


@app.route('/delete-customer', methods=['DELETE'])
@otp_required
def delete_customer():
    """
    Delete a customer based on the provided customer ID.

    Query Parameters:
    - customer_id: ID of the customer to be deleted (required)

    :return: JSON response with a success or error message.
    """
    log_info("Entered /delete-customer endpoint.")
    customer_id = None

    try:
        customer_id = request.args.get('customer_id')

        if not customer_id:
            log_warning("Customer ID not provided in the request.")
            return jsonify({"message": "Customer ID is required."}), 400

        log_info(f"Attempting to delete customer with ID: {customer_id}")

        customer = session.query(HeavyMachineryCustomer).filter_by(customer_id=customer_id).first()

        if not customer:
            log_warning(f"Customer with ID {customer_id} not found.")
            return jsonify({"message": f"Customer with ID {customer_id} not found."}), 404

        customer_details = customer.to_dict()

        session.delete(customer)
        session.commit()
        log_info(f"Customer with ID {customer_id} deleted successfully.")

        deletion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        send_customer_deletion_email(customer_details, deletion_time)

        return jsonify({
            "message": "Customer deleted successfully.",
            "deleted_customer": customer_details
        }), 200

    except Exception as e:
        session.rollback()
        log_error(f"Error deleting customer ID {customer_id}: {str(e)}")
        return jsonify({"message": f"Error deleting customer: {str(e)}"}), 500

    finally:
        session.close()
        log_info("Closed /delete-customer API session.")


if __name__ == "__main__":
    log_info(f"Starting the Flask application {app}.")
    app.run(debug=True)
    log_info("Flask application has stopped.")
