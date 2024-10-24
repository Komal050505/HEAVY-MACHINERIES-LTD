from datetime import datetime

from flask import Flask, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from App.constants import REQUIRED_FIELDS_FOR_HEAVY_MACHINERIES_TABLE, VALID_STATUSES, UPDATABLE_FIELDS
from Db_connections.configurations import session
from Logging_package.logging_utility import log_info, log_error, log_debug
from User_models.tables import Employee
from User_models.tables import HeavyProduct
from Utilities.reusables import otp_required
from email_setup.email_config import RECEIVER_EMAIL
from email_setup.email_operations import generate_heavy_product_email_body, send_email, \
    generate_heavy_product_fetched_body, generate_updated_products_body, generate_deleted_product_body

app = Flask(__name__)


@app.route('/add-heavy-product', methods=['POST'])
@otp_required
def add_heavy_product():
    log_info("Entered /add-heavy-product endpoint. Request method: {}".format(request.method))

    try:
        data = request.json
        log_info("Extracting data from request.")

        for field in REQUIRED_FIELDS_FOR_HEAVY_MACHINERIES_TABLE:
            if field not in data:
                log_error(f"Missing required field: {field}")
                return jsonify({"error": f"Missing required field: {field}"}), 400

        employee_id = data.get('employee_id')
        log_debug(f"Employee ID received: {employee_id}")

        employee = session.query(Employee).filter_by(emp_id=employee_id).first()
        if not employee:
            log_error(f"Employee with ID {employee_id} not found.")
            return jsonify({"error": "Employee not found"}), 404

        log_info(f"Found employee: {employee.emp_first_name} {employee.emp_last_name} (ID: {employee_id})")

        try:
            data['heavy_product_price'] = float(data['heavy_product_price'])
            data['heavy_product_weight'] = float(data['heavy_product_weight'])
            data['heavy_product_horsepower'] = int(data['heavy_product_horsepower'])
            data['heavy_product_fuel_capacity'] = float(data['heavy_product_fuel_capacity'])
            data['heavy_product_operational_hours'] = int(data['heavy_product_operational_hours'])
            data['heavy_product_warranty_period'] = int(data['heavy_product_warranty_period'])
        except (ValueError, TypeError) as e:
            log_error(f"Data type validation error: {str(e)}")
            return jsonify({"error": "Invalid data types for numeric fields."}), 400

        if data.get('status') not in VALID_STATUSES:
            log_error(f"Invalid status value: {data.get('status')}. Valid values are: {VALID_STATUSES}.")
            return jsonify(
                {"error": f"Invalid status value: {data.get('status')}. Valid values are: {VALID_STATUSES}."}), 400

        new_product = HeavyProduct(
            heavy_product_name=data.get('heavy_product_name'),
            heavy_product_type=data.get('heavy_product_type'),
            heavy_product_brand=data.get('heavy_product_brand'),
            heavy_product_model=data.get('heavy_product_model'),
            heavy_product_year_of_manufacture=data.get('heavy_product_year_of_manufacture'),
            heavy_product_price=data['heavy_product_price'],
            heavy_product_weight=data['heavy_product_weight'],
            heavy_product_dimensions=data.get('heavy_product_dimensions'),
            heavy_product_engine_type=data.get('heavy_product_engine_type'),
            heavy_product_horsepower=data['heavy_product_horsepower'],
            heavy_product_fuel_capacity=data['heavy_product_fuel_capacity'],
            heavy_product_operational_hours=data['heavy_product_operational_hours'],
            heavy_product_warranty_period=data['heavy_product_warranty_period'],
            heavy_product_status=data['heavy_product_status'],
            heavy_product_description=data.get('heavy_product_description'),
            heavy_product_image_url=data.get('heavy_product_image_url'),
            employee_id=employee.emp_id,
            employee_name=f"{employee.emp_first_name} {employee.emp_last_name}",
            employee_num=employee.emp_num
        )

        log_info("New HeavyProduct instance created.")

        session.add(new_product)
        session.commit()
        log_info(f"New heavy product added: {new_product.heavy_product_name} (ID: {new_product.heavy_product_id})")

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


@app.route('/get-heavy-products', methods=['GET'])
def get_heavy_products():
    """
    Fetch heavy product details from the database based on query parameters.
    If no parameters are provided, all heavy product records are returned.

    Query parameters:
    heavy_product_id (optional)
    heavy_product_name (optional)
    heavy_product_type (optional)
    heavy_product_brand (optional)
    heavy_product_model (optional)
    heavy_product_year_of_manufacture (optional)
    heavy_product_price (optional)
    heavy_product_weight (optional)
    heavy_product_dimensions (optional)
    heavy_product_engine_type (optional)
    heavy_product_horsepower (optional)
    heavy_product_fuel_capacity (optional)
    heavy_product_operational_hours (optional)
    heavy_product_warranty_period (optional)
    heavy_product_status (optional)
    heavy_product_description (optional)
    heavy_product_created_at (optional)
    heavy_product_updated_at (optional)
    employee_id (optional)

    Returns:
    JSON response with heavy product details and total count.
    """
    log_info("Entered /get-heavy-products endpoint.")
    try:
        product_id = request.args.get('heavy_product_id')
        heavy_product_name = request.args.get('heavy_product_name')
        heavy_product_product_type = request.args.get('heavy_product_type')
        heavy_product_brand = request.args.get('heavy_product_brand')
        heavy_product_model = request.args.get('heavy_product_model')
        heavy_product_year_of_manufacture = request.args.get('heavy_product_year_of_manufacture')
        heavy_product_price = request.args.get('heavy_product_price')
        heavy_product_weight = request.args.get('heavy_product_weight')
        heavy_product_dimensions = request.args.get('heavy_product_dimensions')
        heavy_product_engine_type = request.args.get('heavy_product_engine_type')
        heavy_product_horsepower = request.args.get('heavy_product_horsepower')
        heavy_product_fuel_capacity = request.args.get('heavy_product_fuel_capacity')
        heavy_product_operational_hours = request.args.get('heavy_product_operational_hours')
        heavy_product_warranty_period = request.args.get('heavy_product_warranty_period')
        heavy_product_status = request.args.get('heavy_product_status')
        heavy_product_description = request.args.get('heavy_product_description')
        heavy_product_created_at = request.args.get('heavy_product_created_at')
        heavy_product_updated_at = request.args.get('heavy_product_updated_at')
        heavy_product_employee_id = request.args.get('employee_id')

        log_info(f"Query parameters: {request.args}")

        query = session.query(HeavyProduct)

        if product_id:
            log_debug(f"Filtering by id: {product_id}")
            query = query.filter(HeavyProduct.heavy_product_id == product_id)
        if heavy_product_name:
            log_debug(f"Filtering by name: {heavy_product_name}")
            query = query.filter(HeavyProduct.heavy_product_name.ilike(f'%{heavy_product_name}%'))
        if heavy_product_product_type:
            log_debug(f"Filtering by type: {heavy_product_product_type}")
            query = query.filter(HeavyProduct.heavy_product_type.ilike(f'%{heavy_product_product_type}%'))
        if heavy_product_brand:
            log_debug(f"Filtering by brand: {heavy_product_brand}")
            query = query.filter(HeavyProduct.heavy_product_brand.ilike(f'%{heavy_product_brand}%'))
        if heavy_product_model:
            log_debug(f"Filtering by model: {heavy_product_model}")
            query = query.filter(HeavyProduct.heavy_product_model.ilike(f'%{heavy_product_model}%'))
        if heavy_product_year_of_manufacture:
            log_debug(f"Filtering by year_of_manufacture: {heavy_product_year_of_manufacture}")
            query = query.filter(HeavyProduct.heavy_product_year_of_manufacture == heavy_product_year_of_manufacture)
        if heavy_product_price:
            log_debug(f"Filtering by price: {heavy_product_price}")
            query = query.filter(HeavyProduct.heavy_product_price == heavy_product_price)
        if heavy_product_weight:
            log_debug(f"Filtering by weight: {heavy_product_weight}")
            query = query.filter(HeavyProduct.heavy_product_weight == heavy_product_weight)
        if heavy_product_dimensions:
            log_debug(f"Filtering by dimensions: {heavy_product_dimensions}")
            query = query.filter(HeavyProduct.dimensions.ilike(f'%{heavy_product_dimensions}%'))
        if heavy_product_engine_type:
            log_debug(f"Filtering by engine_type: {heavy_product_engine_type}")
            query = query.filter(HeavyProduct.heavy_product_engine_type.ilike(f'%{heavy_product_engine_type}%'))
        if heavy_product_horsepower:
            log_debug(f"Filtering by horsepower: {heavy_product_horsepower}")
            query = query.filter(HeavyProduct.heavy_product_horsepower == heavy_product_horsepower)
        if heavy_product_fuel_capacity:
            log_debug(f"Filtering by fuel_capacity: {heavy_product_fuel_capacity}")
            query = query.filter(HeavyProduct.heavy_product_fuel_capacity == heavy_product_fuel_capacity)
        if heavy_product_operational_hours:
            log_debug(f"Filtering by operational_hours: {heavy_product_operational_hours}")
            query = query.filter(HeavyProduct.heavy_product_operational_hours == heavy_product_operational_hours)
        if heavy_product_warranty_period:
            log_debug(f"Filtering by warranty_period: {heavy_product_warranty_period}")
            query = query.filter(HeavyProduct.heavy_product_warranty_period == heavy_product_warranty_period)
        if heavy_product_status:
            log_debug(f"Filtering by status: {heavy_product_status}")
            query = query.filter(HeavyProduct.heavy_product_status.ilike(f'%{heavy_product_status}%'))
        if heavy_product_description:
            log_debug(f"Filtering by description: {heavy_product_description}")
            query = query.filter(HeavyProduct.heavy_product_description.ilike(f'%{heavy_product_description}%'))
        if heavy_product_created_at:
            log_debug(f"Filtering by created_at: {heavy_product_created_at}")
            query = query.filter(HeavyProduct.heavy_product_created_at == heavy_product_created_at)
        if heavy_product_updated_at:
            log_debug(f"Filtering by updated_at: {heavy_product_updated_at}")
            query = query.filter(HeavyProduct.heavy_product_updated_at == heavy_product_updated_at)
        if heavy_product_employee_id:
            log_debug(f"Filtering by employee_id: {heavy_product_employee_id}")
            query = query.filter(HeavyProduct.heavy_product_employee_id == heavy_product_employee_id)

        heavy_products = query.all()
        total_count = query.count()

        product_list = [product.to_dict() for product in heavy_products]
        log_info(f"Fetched {len(product_list)} heavy product(s).")

        email_body = generate_heavy_product_fetched_body(product_list, total_count)
        send_email(RECEIVER_EMAIL, "Heavy Products Fetched", email_body)

        return jsonify({"total_count": total_count, "heavy_products": product_list}), 200

    except Exception as e:
        session.rollback()
        log_error(f"Error fetching heavy products: {str(e)}")
        return jsonify({"message": f"Error fetching heavy products: {str(e)}"}), 500
    finally:
        session.close()
        log_info("Closed /get-heavy-products endpoint.")


@app.route('/update-heavy-product', methods=['PUT'])
@otp_required
def update_heavy_product():
    """
    Update details of a heavy product by its ID. Fields are provided through the raw JSON body and
    validated against the list of allowed fields.

    The API accepts the following fields for update:
    product_id (required)
    heavy_product_name (optional)
    heavy_product_type (optional)
    heavy_product_brand (optional)
    heavy_product_model (optional)
    heavy_product_year_of_manufacture (optional)
    heavy_product_price (optional)
    heavy_product_weight (optional)
    heavy_product_dimensions (optional)
    heavy_product_engine_type (optional)
    heavy_product_horsepower (optional)
    heavy_product_fuel_capacity (optional)
    heavy_product_operational_hours (optional)
    heavy_product_warranty_period (optional)
    heavy_product_status (optional)
    heavy_product_description (optional)
    heavy_product_image_url (optional)
    employee_id (optional)
    employee_name (optional)
    employee_num (optional)

    The `product_id` must be provided to identify the product that needs to be updated.
    All other fields are optional, and only those included in the request body will be updated.

    :return: Returns the product which is successfully updated along with employee details.
    """
    product_id = None
    employee = None

    try:
        data = request.get_json()
        log_info(f"Received update request data: {data}")

        product_id = data.get('heavy_product_id')
        if not product_id:
            log_error("Product ID is missing from the request body.")
            return jsonify({"error": "Product ID is required"}), 400

        log_info(f"Fetching product with ID: {product_id}")

        product = session.query(HeavyProduct).filter_by(heavy_product_id=product_id).first()
        if not product:
            log_error(f"Product with ID {product_id} not found.")
            return jsonify({"error": "Product not found"}), 404

        product_name = product.heavy_product_name
        log_info(f"Product {product_id} found in the database.")

        updated_fields = {}
        for field in data:
            if field in UPDATABLE_FIELDS:
                setattr(product, field, data[field])
                updated_fields[field] = data[field]

        if not updated_fields:
            log_error("No valid fields were provided for update.")
            return jsonify({"error": "No valid fields provided for update"}), 400

        employee_id = data.get('employee_id')
        if employee_id:
            log_debug(f"Employee ID received for update: {employee_id}")

            employee = session.query(Employee).filter_by(emp_id=employee_id).first()
            if not employee:
                log_error(f"Employee with ID {employee_id} not found.")
                return jsonify({"error": "Employee not found"}), 404

            log_info(f"Found employee: {employee.emp_first_name} {employee.emp_last_name} (ID: {employee_id})")
            # Update employee details
            product.employee_name = f"{employee.emp_first_name} {employee.emp_last_name}"
            product.employee_num = employee.emp_num
            updated_fields['employee_name'] = product.employee_name
            updated_fields['employee_num'] = product.employee_num

        log_info(f"Updating product {product_id} with fields: {updated_fields}")

        session.commit()
        log_info(f"Product {product_id} updated successfully in the database.")

        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email_body = generate_updated_products_body(updated_fields, update_time, employee, product_id, product_name)
        send_email(
            too_email=RECEIVER_EMAIL,
            subject=f"Product {product_id} Update Notification",
            body=email_body
        )
        log_info(f"Email notification sent for product {product_id} update.")

        return jsonify({
            "message": "Product updated successfully",
            "product": product.to_dict(),
            "product_id": product.heavy_product_id,
            "product_name": product.heavy_product_name,
            "employee_name": product.employee_name,
            "employee_num": product.employee_num
        }), 200

    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Database error updating product {product_id}: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500

    except Exception as e:
        session.rollback()
        log_error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

    finally:
        session.close()
        log_info(f"Update heavy product process completed for product ID {product_id}.")


@app.route('/delete-heavy-product', methods=['DELETE'])
@otp_required
def delete_heavy_product():
    """
    Delete a heavy product by its ID. The product ID is provided through query parameters.

    :return: Returns a confirmation message if the product is successfully deleted.
    """
    product_id = None

    try:
        product_id = request.args.get('heavy_product_id')
        if not product_id:
            log_error("Product ID is missing from the query parameters.")
            return jsonify({"error": "Product ID is required"}), 400

        log_info(f"Fetching product with ID: {product_id}")

        product = session.query(HeavyProduct).filter_by(heavy_product_id=product_id).first()
        if not product:
            log_error(f"Product with ID {product_id} not found.")
            return jsonify({"error": "Product not found"}), 404

        product_details = {
            "product_id": product.heavy_product_id,
            "name": product.heavy_product_name,
            "type": product.heavy_product_type,
            "brand": product.heavy_product_brand,
            "model": product.heavy_product_model,
            "year_of_manufacture": product.heavy_product_year_of_manufacture,
            "price": product.heavy_product_price,
            "weight": product.heavy_product_weight,
            "dimensions": product.heavy_product_dimensions,
            "engine_type": product.heavy_product_engine_type,
            "horsepower": product.heavy_product_horsepower,
            "fuel_capacity": product.heavy_product_fuel_capacity,
            "operational_hours": product.heavy_product_operational_hours,
            "warranty_period": product.heavy_product_warranty_period,
            "status": product.heavy_product_status,
            "description": product.heavy_product_description,
            "image_url": product.heavy_product_image_url,
            "employee_id": product.employee_id,
            "employee_name": product.employee_name,
            "employee_num": product.employee_num,
        }

        log_info(f"Deleting product {product_id} from the database.")
        session.delete(product)
        session.commit()
        log_info(f"Product {product_id} deleted successfully from the database.")

        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email_body = generate_deleted_product_body(product_details, update_time)
        send_email(
            too_email=RECEIVER_EMAIL,
            subject=f"Product {product_id} Deletion Notification",
            body=email_body
        )
        log_info(f"Email notification sent for product {product_id} deletion.")

        return jsonify({
            "message": "Product deleted successfully",
            "product": product_details  # Include complete product details in response
        }), 200

    except SQLAlchemyError as e:
        session.rollback()
        log_error(f"Database error deleting product {product_id}: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500

    except Exception as e:
        session.rollback()
        log_error(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

    finally:
        session.close()
        log_info(f"Delete heavy product process completed for product ID {product_id}.")


if __name__ == "__main__":
    log_info(f"Starting the Flask application {app}.")
    app.run(debug=True)
    log_info("Flask application has stopped.")
