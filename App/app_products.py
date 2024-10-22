from flask import Flask, request, jsonify

from App.constants import REQUIRED_FIELDS_FOR_HEAVY_MACHINERIES_TABLE, VALID_STATUSES
from Db_connections.configurations import session
from Logging_package.logging_utility import log_info, log_error, log_debug
from User_models.tables import Employee
from User_models.tables import HeavyProduct
from Utilities.reusables import otp_required
from email_setup.email_config import RECEIVER_EMAIL
from email_setup.email_operations import generate_heavy_product_email_body, send_email

app = Flask(__name__)


@app.route('/add-heavy-product', methods=['POST'])
@otp_required
def add_heavy_product():
    log_info("Entered /add-heavy-product endpoint. Request method: {}".format(request.method))

    try:
        data = request.json
        log_info("Extracting data from request.")

        # Check for missing required fields
        for field in REQUIRED_FIELDS_FOR_HEAVY_MACHINERIES_TABLE:
            if field not in data:
                log_error(f"Missing required field: {field}")
                return jsonify({"error": f"Missing required field: {field}"}), 400

        employee_id = data.get('employee_id')
        log_debug(f"Employee ID received: {employee_id}")

        employee = session.query(Employee).filter_by(id=employee_id).first()
        if not employee:
            log_error(f"Employee with ID {employee_id} not found.")
            return jsonify({"error": "Employee not found"}), 404

        log_info(f"Found employee: {employee.first_name} {employee.last_name} (ID: {employee_id})")

        # Validate numeric fields
        try:
            data['price'] = float(data['price'])
            data['weight'] = float(data['weight'])
            data['horsepower'] = int(data['horsepower'])
            data['fuel_capacity'] = float(data['fuel_capacity'])
            data['operational_hours'] = int(data['operational_hours'])
            data['warranty_period'] = int(data['warranty_period'])
        except (ValueError, TypeError) as e:
            log_error(f"Data type validation error: {str(e)}")
            return jsonify({"error": "Invalid data types for numeric fields."}), 400

        # Validate the status field
        if data.get('status') not in VALID_STATUSES:
            log_error(f"Invalid status value: {data.get('status')}. Valid values are: {VALID_STATUSES}.")
            return jsonify(
                {"error": f"Invalid status value: {data.get('status')}. Valid values are: {VALID_STATUSES}."}), 400

        # Create a new HeavyProduct instance
        new_product = HeavyProduct(
            name=data.get('name'),
            type=data.get('type'),
            brand=data.get('brand'),
            model=data.get('model'),
            year_of_manufacture=data.get('year_of_manufacture'),
            price=data['price'],
            weight=data['weight'],
            dimensions=data.get('dimensions'),
            engine_type=data.get('engine_type'),
            horsepower=data['horsepower'],
            fuel_capacity=data['fuel_capacity'],
            operational_hours=data['operational_hours'],
            warranty_period=data['warranty_period'],
            status=data['status'],
            description=data.get('description'),
            image_url=data.get('image_url'),
            employee_id=employee.id,
            employee_name=f"{employee.first_name} {employee.last_name}",
            employee_num=employee.emp_num
        )

        log_info("New HeavyProduct instance created.")

        session.add(new_product)
        session.commit()
        log_info(f"New heavy product added: {new_product.name} (ID: {new_product.id})")

        email_subject = "New Heavy Product Added"
        email_body = generate_heavy_product_email_body(new_product, employee)
        send_email(RECEIVER_EMAIL, "New Product Added", email_body)
        log_info(f"Email notification sent successfully with email subject: {email_subject} and body: {email_body}.")
        return jsonify({"Success Message": "New Product Added Successfully"}, new_product.to_dict()), 201

    except Exception as e:
        log_error(f"Error adding new heavy product: {str(e)}")
        return jsonify({"error": "An error occurred while adding the product"}), 500

    finally:
        session.close()
        log_info("Database session closed.")


if __name__ == "__main__":
    log_info(f"Starting the Flask application {app}.")
    app.run(debug=True)
    log_info("Flask application has stopped.")
