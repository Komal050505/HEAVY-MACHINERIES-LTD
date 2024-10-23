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

        employee = session.query(Employee).filter_by(id=employee_id).first()
        if not employee:
            log_error(f"Employee with ID {employee_id} not found.")
            return jsonify({"error": "Employee not found"}), 404

        log_info(f"Found employee: {employee.first_name} {employee.last_name} (ID: {employee_id})")

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

        if data.get('status') not in VALID_STATUSES:
            log_error(f"Invalid status value: {data.get('status')}. Valid values are: {VALID_STATUSES}.")
            return jsonify(
                {"error": f"Invalid status value: {data.get('status')}. Valid values are: {VALID_STATUSES}."}), 400

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


@app.route('/get-heavy-products', methods=['GET'])
def get_heavy_products():
    """
    Fetch heavy product details from the database based on query parameters.
    If no parameters are provided, all heavy product records are returned.

    Query parameters:
    id (optional)
    name (optional)
    type (optional)
    brand (optional)
    model (optional)
    year_of_manufacture (optional)
    price (optional)
    weight (optional)
    dimensions (optional)
    engine_type (optional)
    horsepower (optional)
    fuel_capacity (optional)
    operational_hours (optional)
    warranty_period (optional)
    status (optional)
    description (optional)
    created_at (optional)
    updated_at (optional)
    employee_id (optional)

    Returns:
    JSON response with heavy product details and total count.
    """
    log_info("Entered /get-heavy-products endpoint.")
    try:
        product_id = request.args.get('id')
        name = request.args.get('name')
        product_type = request.args.get('type')
        brand = request.args.get('brand')
        model = request.args.get('model')
        year_of_manufacture = request.args.get('year_of_manufacture')
        price = request.args.get('price')
        weight = request.args.get('weight')
        dimensions = request.args.get('dimensions')
        engine_type = request.args.get('engine_type')
        horsepower = request.args.get('horsepower')
        fuel_capacity = request.args.get('fuel_capacity')
        operational_hours = request.args.get('operational_hours')
        warranty_period = request.args.get('warranty_period')
        status = request.args.get('status')
        description = request.args.get('description')
        created_at = request.args.get('created_at')
        updated_at = request.args.get('updated_at')
        employee_id = request.args.get('employee_id')

        log_info(f"Query parameters: {request.args}")

        query = session.query(HeavyProduct)

        if product_id:
            log_debug(f"Filtering by id: {product_id}")
            query = query.filter(HeavyProduct.id == product_id)
        if name:
            log_debug(f"Filtering by name: {name}")
            query = query.filter(HeavyProduct.name.ilike(f'%{name}%'))
        if product_type:
            log_debug(f"Filtering by type: {product_type}")
            query = query.filter(HeavyProduct.type.ilike(f'%{product_type}%'))
        if brand:
            log_debug(f"Filtering by brand: {brand}")
            query = query.filter(HeavyProduct.brand.ilike(f'%{brand}%'))
        if model:
            log_debug(f"Filtering by model: {model}")
            query = query.filter(HeavyProduct.model.ilike(f'%{model}%'))
        if year_of_manufacture:
            log_debug(f"Filtering by year_of_manufacture: {year_of_manufacture}")
            query = query.filter(HeavyProduct.year_of_manufacture == year_of_manufacture)
        if price:
            log_debug(f"Filtering by price: {price}")
            query = query.filter(HeavyProduct.price == price)
        if weight:
            log_debug(f"Filtering by weight: {weight}")
            query = query.filter(HeavyProduct.weight == weight)
        if dimensions:
            log_debug(f"Filtering by dimensions: {dimensions}")
            query = query.filter(HeavyProduct.dimensions.ilike(f'%{dimensions}%'))
        if engine_type:
            log_debug(f"Filtering by engine_type: {engine_type}")
            query = query.filter(HeavyProduct.engine_type.ilike(f'%{engine_type}%'))
        if horsepower:
            log_debug(f"Filtering by horsepower: {horsepower}")
            query = query.filter(HeavyProduct.horsepower == horsepower)
        if fuel_capacity:
            log_debug(f"Filtering by fuel_capacity: {fuel_capacity}")
            query = query.filter(HeavyProduct.fuel_capacity == fuel_capacity)
        if operational_hours:
            log_debug(f"Filtering by operational_hours: {operational_hours}")
            query = query.filter(HeavyProduct.operational_hours == operational_hours)
        if warranty_period:
            log_debug(f"Filtering by warranty_period: {warranty_period}")
            query = query.filter(HeavyProduct.warranty_period == warranty_period)
        if status:
            log_debug(f"Filtering by status: {status}")
            query = query.filter(HeavyProduct.status.ilike(f'%{status}%'))
        if description:
            log_debug(f"Filtering by description: {description}")
            query = query.filter(HeavyProduct.description.ilike(f'%{description}%'))
        if created_at:
            log_debug(f"Filtering by created_at: {created_at}")
            query = query.filter(HeavyProduct.created_at == created_at)
        if updated_at:
            log_debug(f"Filtering by updated_at: {updated_at}")
            query = query.filter(HeavyProduct.updated_at == updated_at)
        if employee_id:
            log_debug(f"Filtering by employee_id: {employee_id}")
            query = query.filter(HeavyProduct.employee_id == employee_id)

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
    name (optional)
    type (optional)
    brand (optional)
    model (optional)
    year_of_manufacture (optional)
    price (optional)
    weight (optional)
    dimensions (optional)
    engine_type (optional)
    horsepower (optional)
    fuel_capacity (optional)
    operational_hours (optional)
    warranty_period (optional)
    status (optional)
    description (optional)
    image_url (optional)
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

        product_id = data.get('id')
        if not product_id:
            log_error("Product ID is missing from the request body.")
            return jsonify({"error": "Product ID is required"}), 400

        log_info(f"Fetching product with ID: {product_id}")

        product = session.query(HeavyProduct).filter_by(id=product_id).first()
        if not product:
            log_error(f"Product with ID {product_id} not found.")
            return jsonify({"error": "Product not found"}), 404

        product_name = product.name
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

            employee = session.query(Employee).filter_by(id=employee_id).first()
            if not employee:
                log_error(f"Employee with ID {employee_id} not found.")
                return jsonify({"error": "Employee not found"}), 404

            log_info(f"Found employee: {employee.first_name} {employee.last_name} (ID: {employee_id})")
            # Update employee details
            product.employee_name = f"{employee.first_name} {employee.last_name}"
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
            "product_id": product.id,
            "product_name": product.name,
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
        product_id = request.args.get('id')
        if not product_id:
            log_error("Product ID is missing from the query parameters.")
            return jsonify({"error": "Product ID is required"}), 400

        log_info(f"Fetching product with ID: {product_id}")

        product = session.query(HeavyProduct).filter_by(id=product_id).first()
        if not product:
            log_error(f"Product with ID {product_id} not found.")
            return jsonify({"error": "Product not found"}), 404

        product_details = {
            "product_id": product.id,
            "name": product.name,
            "type": product.type,
            "brand": product.brand,
            "model": product.model,
            "year_of_manufacture": product.year_of_manufacture,
            "price": product.price,
            "weight": product.weight,
            "dimensions": product.dimensions,
            "engine_type": product.engine_type,
            "horsepower": product.horsepower,
            "fuel_capacity": product.fuel_capacity,
            "operational_hours": product.operational_hours,
            "warranty_period": product.warranty_period,
            "status": product.status,
            "description": product.description,
            "image_url": product.image_url,
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
