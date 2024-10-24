import traceback
import uuid
from datetime import datetime

import pytz
from flask import jsonify, request, Flask
from sqlalchemy.exc import SQLAlchemyError

from Db_connections.configurations import session
from Logging_package.logging_utility import log_info, log_error, log_debug, log_warning
from User_models.tables import HeavyMachineryOpportunity, Account, HeavyMachineriesDealer, Employee, HeavyProduct
from Utilities.reusables import otp_required, get_opportunity_stage, get_currency_conversion, validate_probability, \
    validate_stage
from email_setup.email_operations import notify_failure, notify_success, notify_opportunity_details, \
    send_opportunity_update_email, construct_success_message

app = Flask(__name__)


@app.route('/new-customer', methods=["POST"])
@otp_required
def create_new_customer():
    """
    Creates a new customer in the opportunity table.
    :return: JSON response with email notifications and detailed customer information.
    """
    log_info("Received request to create new customer")
    try:
        payload = request.get_json()
        log_debug(f"Request payload: {payload}")

        opportunity_id = str(uuid.uuid4())
        log_info(f"Generated opportunity_id: {opportunity_id}")

        created_date = datetime.now(pytz.timezone('Asia/Kolkata'))
        payload.update({'created_date': created_date, 'opportunity_id': opportunity_id})
        log_info(f"Payload after adding created_date and opportunity_id: {payload}")

        account_name = payload.get("account_name")
        account = session.query(Account).filter_by(account_name=account_name).first()

        if not account:
            new_account_id = str(uuid.uuid4())

            new_account = Account(account_id=new_account_id, account_name=account_name)

            session.add(new_account)
            session.commit()
            log_info(f"New account added: {account_name}")

            account_creation_message = (f"New account added to the database:\n"
                                        f"Account Name: {account_name}")
            notify_success("New Account Added", account_creation_message)
        else:
            log_info(f"Account found: {account_name}")

        dealer_id = payload.get("dealer_id")
        dealer_code = payload.get("dealer_code")
        opportunity_owner = payload.get("opportunity_owner")

        dealer = session.query(HeavyMachineriesDealer).filter_by(dealer_id=dealer_id, dealer_code=dealer_code,
                                                                 opportunity_owner=opportunity_owner
                                                                 ).first()

        if not dealer:
            log_info(
                f"Dealer with ID {dealer_id} not found, but no need to create new dealer. Proceeding with existing dealers.")
        else:
            log_info(f"Dealer found: {dealer_id}, {dealer_code}, {opportunity_owner}")

        close_date_str = payload.get("close_date")
        if close_date_str:
            try:
                close_date = datetime.strptime(close_date_str, "%Y-%m-%d %H:%M:%S")
                log_info(f"Parsed close_date: {close_date}")
            except ValueError as e:
                session.rollback()
                error_message = f"Invalid date format for close_date: {str(e)}"
                log_error(error_message)
                detailed_error_message = f"Failed to create customer due to invalid date format.\nError: {str(e)}"
                notify_failure("Customer Creation Failed", detailed_error_message)
                return jsonify({"error": error_message}), 400
        else:
            close_date = None
            log_info("No close_date provided, set to None")

        probability = payload.get("probability")

        if probability is not None:
            try:
                stage = get_opportunity_stage(probability)
                log_info(f"Determined stage from probability: {stage}")
            except ValueError as e:
                session.rollback()
                error_message = f"Invalid probability value: {str(e)}"
                log_error(error_message)
                notify_failure("Customer Creation Failed", error_message)
                return jsonify({"error": error_message}), 400
        else:
            stage = payload.get("stage", "Unknown")
            log_info(f"No probability provided, defaulting stage to: {stage}")

        amount = payload.get("amount")
        if amount:
            currency_conversions = get_currency_conversion(amount)
            log_info(f"Currency conversions for amount {amount}: {currency_conversions}")
        else:
            currency_conversions = {}
            log_info("No amount provided, currency conversions set to empty")

        employee_id = payload.get('employee_id')
        log_info(f"Looking for employee with ID: {employee_id}")

        if employee_id:
            employee = session.query(Employee).filter_by(emp_id=employee_id).first()  # Make sure 'id' is UUID
            if not employee:
                error_message = f"Employee with ID {employee_id} not found."
                log_error(error_message)
                notify_failure("Customer Creation Failed", error_message)
                return jsonify({"error": error_message}), 404
            else:
                log_info(f"Employee found: {employee.emp_first_name} {employee.emp_last_name}, ID: {employee.emp_num}")
        else:
            error_message = "Employee ID is required."
            log_error(error_message)
            notify_failure("Customer Creation Failed", error_message)
            return jsonify({"error": error_message}), 400

        product_id = payload.get("product_id")
        if product_id:
            product = session.query(HeavyProduct).filter_by(heavy_product_id=product_id).first()
            if product:
                log_info(f"Product found: {product.heavy_product_name}")
                payload.update({
                    "product_id": str(product.heavy_product_id),
                    "product_name": product.heavy_product_name,
                    "product_brand": product.heavy_product_brand,
                    "product_model": product.heavy_product_model,
                    "product_image_url": product.heavy_product_image_url
                })
            else:
                log_error(f"Product with ID {product_id} not found.")
                return jsonify({"error": "Product not found."}), 400
        else:
            log_error("Product ID is required.")
            return jsonify({"error": "Product ID is required."}), 400

        new_opportunity = HeavyMachineryOpportunity(
            opportunity_id=opportunity_id,
            opportunity_name=payload.get("opportunity_name"),
            account_name=account_name,
            close_date=close_date,
            amount=amount,
            description=payload.get("description"),
            dealer_id=dealer_id,
            dealer_code=dealer_code,
            stage=stage,
            probability=probability,
            next_step=payload.get("next_step"),
            created_date=created_date,
            usd=currency_conversions.get("USD"),
            aus=currency_conversions.get("AUD"),
            cad=currency_conversions.get("CAD"),
            jpy=currency_conversions.get("JPY"),
            eur=currency_conversions.get("EUR"),
            gbp=currency_conversions.get("GBP"),
            cny=currency_conversions.get("CNY"),
            amount_in_words=str(amount),
            employee_id=employee_id,
            product_id=payload["product_id"],  # Ensure product_id is set
            product_name=payload["product_name"],
            product_brand=payload["product_brand"],
            product_model=payload["product_model"],
            product_image_url=payload["product_image_url"]

        )
        log_info(f"New Opportunity object created: {new_opportunity}")

        session.add(new_opportunity)
        session.commit()
        log_info(f"Opportunity created successfully: {opportunity_id}")

        customer_details = new_opportunity.serialize_to_dict()
        log_info(f"Serialized customer details: {customer_details}")

        formatted_currency_conversions = "\n".join(f"{key}: {value}" for key, value in currency_conversions.items())

        employee_name = f"{employee.first_name} {employee.last_name}"
        employee_num = employee.emp_num

        success_message = (f"Customer created successfully.\n\n\n"
                           f"Opportunity ID: {opportunity_id}\n\n"
                           f"Opportunity Name: {payload.get('opportunity_name')}\n\n"
                           f"Account Name: {account_name}\n\n"
                           f"Close Date: {close_date.strftime('%Y-%m-%d %H:%M:%S') if close_date else None}\n\n"
                           f"Amount: {payload.get('amount')}\n\n"
                           f"Stage: {stage}\n\n"
                           f"Probability: {payload.get('probability')}\n\n"
                           f"Currency Conversions:\n{formatted_currency_conversions}\n\n"
                           f"Employee ID: {employee_id}\n\n"
                           f"Employee Name: {employee_name}\n\n"
                           f"Employee Number: {employee_num}\n\n"
                           f"Product Id: {payload['product_id']}\n\n"
                           f"Product Name: {payload['product_name']}\n\n"
                           f"Product Brand: {payload['product_brand']}\n\n"
                           f"Product product_model: {payload['product_model']}\n\n"
                           f"Product product_image_url: {payload['product_image_url']}\n\n"
                           f"Created Date: {created_date.strftime('%Y-%m-%d %H:%M:%S')}")

        notify_success("Customer Creation Successful", success_message)

        return jsonify({
            "message": "Created successfully",
            "customer_details": customer_details
        }), 201

    except SQLAlchemyError as e:
        session.rollback()
        error_message = f"Error in creating customer: {str(e)}"
        log_error(error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    except Exception as e:
        session.rollback()
        error_message = f"Error in creating customer: {str(e)}"
        log_error(error_message)
        detailed_error_message = f"Failed to create customer due to an internal server error.\nDetails: {str(e)}"
        notify_failure("Customer Creation Failed", detailed_error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    finally:
        session.close()
        log_info("End of create_new_customer function")


@app.route('/get-opportunities', methods=['GET'])
def get_opportunities():
    """
    Fetches opportunities from the opportunity table based on query parameters.
    :return: JSON response with filtered opportunity details and total count.
    """
    log_info("Received request to get opportunities with query parameters")

    try:
        opportunity_id = request.args.get('opportunity_id')
        opportunity_name = request.args.get('opportunity_name', '').strip()
        account_name = request.args.get('account_name', '').strip()
        stage = request.args.get('stage', '').strip()
        probability_min = request.args.get('probability_min', type=int)
        probability_max = request.args.get('probability_max', type=int)
        created_date_start = request.args.get('created_date_start')
        close_date_end = request.args.get('close_date_end')
        amount_min = request.args.get('amount_min', type=float)
        amount_max = request.args.get('amount_max', type=float)

        employee_id = request.args.get('employee_id', '').strip()
        product_id = request.args.get('product_id', '').strip()
        product_name = request.args.get('product_name', '').strip()
        product_brand = request.args.get('product_brand', '').strip()
        product_model = request.args.get('product_model', '').strip()

        log_info(f"Query parameters retrieved: opportunity_id={opportunity_id}, opportunity_name={opportunity_name}, "
                 f"account_name={account_name}, stage={stage}, probability_min={probability_min}, "
                 f"probability_max={probability_max}, created_date_start={created_date_start}, "
                 f"close_date_end={close_date_end}, amount_min={amount_min}, amount_max={amount_max}, "
                 f"employee_id={employee_id}, "
                 f"product_id={product_id}, product_name={product_name}, "
                 f"product_brand={product_brand}, product_model={product_model}")

        if created_date_start:
            created_date_start = datetime.fromisoformat(created_date_start.replace('Z', '+00:00'))
            log_info(f"Parsed created_date_start: {created_date_start}")

        if close_date_end:
            close_date_end = datetime.fromisoformat(close_date_end.replace('Z', '+00:00'))
            log_info(f"Parsed close_date_end: {close_date_end}")

        if probability_min is not None and not validate_probability(probability_min):
            error_message = f"Invalid minimum probability: {probability_min}. Must be between 0 and 100"
            log_error(error_message)
            raise ValueError(error_message)

        if probability_max is not None and not validate_probability(probability_max):
            error_message = f"Invalid maximum probability: {probability_max}. Must be between 0 and 100"
            log_error(error_message)
            raise ValueError(error_message)

        if probability_min is not None and probability_max is not None and probability_min > probability_max:
            error_message = "Minimum probability cannot be greater than maximum probability"
            log_error(error_message)
            raise ValueError(error_message)

        if stage:
            stage = validate_stage(stage)
            log_info(f"Validated stage: {stage}")

        query = session.query(HeavyMachineryOpportunity)
        log_info("Constructed initial query")

        if opportunity_id:
            query = query.filter(HeavyMachineryOpportunity.opportunity_id == opportunity_id)
            log_info(f"Applied filter: opportunity_id = {opportunity_id}")

        if opportunity_name:
            if len(opportunity_name) > 255:
                error_message = "Opportunity name is too long. Maximum length is 255 characters."
                log_error(error_message)
                raise ValueError(error_message)
            query = query.filter(HeavyMachineryOpportunity.opportunity_name.ilike(f'%{opportunity_name}%'))
            log_info(f"Applied filter: opportunity_name case-insensitive contains '{opportunity_name}'")

        if account_name:
            if len(account_name) > 255:
                error_message = "Account name is too long. Maximum length is 255 characters."
                log_error(error_message)
                raise ValueError(error_message)
            query = query.filter(HeavyMachineryOpportunity.account_name.ilike(f'%{account_name}%'))
            log_info(f"Applied filter: account_name case-insensitive contains '{account_name}'")

        if stage:
            query = query.filter(HeavyMachineryOpportunity.stage.ilike(f'%{stage}%'))
            log_info(f"Applied filter: stage case-insensitive = {stage}")

        if probability_min is not None:
            query = query.filter(HeavyMachineryOpportunity.probability >= probability_min)
            log_info(f"Applied filter: probability >= {probability_min}")

        if probability_max is not None:
            query = query.filter(HeavyMachineryOpportunity.probability <= probability_max)
            log_info(f"Applied filter: probability <= {probability_max}")

        if created_date_start:
            query = query.filter(HeavyMachineryOpportunity.created_date >= created_date_start)
            log_info(f"Applied filter: created_date >= {created_date_start}")

        if close_date_end:
            query = query.filter(HeavyMachineryOpportunity.close_date <= close_date_end)
            log_info(f"Applied filter: close_date <= {close_date_end}")

        if amount_min is not None:
            query = query.filter(HeavyMachineryOpportunity.amount >= amount_min)
            log_info(f"Applied filter: amount >= {amount_min}")

        if amount_max is not None:
            query = query.filter(HeavyMachineryOpportunity.amount <= amount_max)
            log_info(f"Applied filter: amount <= {amount_max}")

        if employee_id:
            query = query.filter(HeavyMachineryOpportunity.employee_id == employee_id)
            log_info(f"Applied filter: employee_id = {employee_id}")

        if product_id:
            query = query.filter(HeavyMachineryOpportunity.product_id == product_id)
            log_info(f"Applied filter: product_id = {product_id}")

        if product_name:
            query = query.filter(HeavyMachineryOpportunity.product_name.ilike(f'%{product_name}%'))
            log_info(f"Applied filter: product_name case-insensitive contains '{product_name}'")

        if product_brand:
            query = query.filter(HeavyMachineryOpportunity.product_brand.ilike(f'%{product_brand}%'))
            log_info(f"Applied filter: product_brand case-insensitive contains '{product_brand}'")

        if product_model:
            query = query.filter(HeavyMachineryOpportunity.product_model.ilike(f'%{product_model}%'))
            log_info(f"Applied filter: product_model case-insensitive contains '{product_model}'")

        opportunities = query.all()
        total_count = len(opportunities)
        log_info(f"Fetched {total_count} opportunities based on query parameters")

        opportunities_list = [opportunity.serialize_to_dict() for opportunity in opportunities]
        log_info("Serialized opportunities to dictionary format")

        notify_opportunity_details("Get Opportunities Successful", opportunities_list, total_count)

        return jsonify({"Opportunities": opportunities_list, "Total count of opportunities": total_count}), 200

    except ValueError as ve:
        session.rollback()
        error_message = f"Validation error: {str(ve)}"
        log_error(error_message)
        notify_failure("Get Opportunities Validation Failed", error_message)
        return jsonify({"error": "Bad Request", "details": error_message}), 400

    except SQLAlchemyError as sae:
        session.rollback()
        error_message = f"Database error: {str(sae)}"
        log_error(error_message)
        log_error(traceback.format_exc())
        notify_failure("Get Opportunities Database Error", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    except Exception as e:
        session.rollback()
        error_message = f"Error in fetching opportunities: {str(e)}"
        log_error(error_message)
        notify_failure("Get Opportunities Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    finally:
        session.close()
        log_info("End of get_opportunities function")


@app.route('/update_opportunity', methods=['PUT'])
@otp_required
def update_opportunity():
    try:
        data = request.json

        opportunity_id = data.get('opportunity_id')
        if not opportunity_id:
            log_error("Opportunity ID missing in the request")
            return jsonify({'error': 'Opportunity ID is required'}), 400

        opportunity = session.query(HeavyMachineryOpportunity).filter_by(opportunity_id=opportunity_id).first()

        if not opportunity:
            log_warning(f"Opportunity with ID {opportunity_id} not found")
            return jsonify({'error': 'Opportunity not found'}), 404

        log_info(f"Current Opportunity Details: {opportunity.serialize_to_dict()}")

        updated_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%I:%M %p, %B %d, %Y')

        opportunity.opportunity_name = data.get('opportunity_name', opportunity.opportunity_name)
        opportunity.account_name = data.get('account_name', opportunity.account_name)
        opportunity.close_date = datetime.fromisoformat(data.get('close_date')) if data.get(
            'close_date') else opportunity.close_date

        opportunity.amount = data.get('amount', opportunity.amount)
        opportunity.amount_in_words = data.get('amount_in_words', opportunity.amount_in_words)
        opportunity.description = data.get('description', opportunity.description)
        opportunity.dealer_id = data.get('dealer_id', opportunity.dealer_id)
        opportunity.dealer_code = data.get('dealer_code', opportunity.dealer_code)
        opportunity.stage = data.get('stage', opportunity.stage)
        opportunity.probability = data.get('probability', opportunity.probability)
        opportunity.next_step = data.get('next_step', opportunity.next_step)

        opportunity.employee_id = data.get('employee_id', opportunity.employee_id)
        opportunity.product_id = data.get('product_id', opportunity.product_id)
        opportunity.product_name = data.get('product_name', opportunity.product_name)
        opportunity.product_brand = data.get('product_brand', opportunity.product_brand)
        opportunity.product_model = data.get('product_model', opportunity.product_model)
        opportunity.product_image_url = data.get('product_image_url', opportunity.product_image_url)

        opportunity.usd = data.get('usd', opportunity.usd)
        opportunity.aus = data.get('aus', opportunity.aus)
        opportunity.cad = data.get('cad', opportunity.cad)
        opportunity.jpy = data.get('jpy', opportunity.jpy)
        opportunity.eur = data.get('eur', opportunity.eur)
        opportunity.gbp = data.get('gbp', opportunity.gbp)
        opportunity.cny = data.get('cny', opportunity.cny)

        session.commit()

        log_info(f"Updated Opportunity Details: {opportunity.serialize_to_dict()}")

        send_opportunity_update_email(opportunity, updated_time)

        return jsonify({
            'message': 'Opportunity updated successfully',
            'updated_time': updated_time,
            'opportunity_details': opportunity.serialize_to_dict()
        }), 200

    except Exception as e:
        session.rollback()
        log_error(f"Error while updating opportunity: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        session.close()
        log_info("End of update_opportunity function")


@app.route('/delete-opportunity', methods=["DELETE"])
@otp_required
def delete_opportunity():
    """
    Deletes a customer from the opportunity table based on query parameters.
    :return: JSON response with email notifications and result of deletion.
    """
    log_info("Received request to delete customer")
    try:
        opportunity_id = request.args.get("opportunity_id")
        account_name = request.args.get("account_name")
        dealer_id = request.args.get("dealer_id")
        dealer_code = request.args.get("dealer_code")
        opportunity_name = request.args.get("opportunity_name")
        stage = request.args.get("stage")
        probability = request.args.get("probability", type=int)
        close_date = request.args.get("close_date")

        if not any([opportunity_id, account_name, dealer_id, dealer_code, opportunity_name, stage, probability,
                    close_date]):
            error_message = ("At least one query parameter (opportunity_id, account_name, dealer_id, dealer_code, "
                             "opportunity_name, stage, probability, or close_date) is required for deletion.")
            log_error(error_message)
            notify_failure("Customer Deletion Failed", "Failed to delete customer due to missing query parameters.")
            return jsonify({"error": error_message}), 400

        if close_date:
            try:
                close_date = datetime.strptime(close_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                error_message = "Invalid close_date format. Use 'YYYY-MM-DD HH:MM:SS'."
                log_error(error_message)
                notify_failure("Customer Deletion Failed",
                               "Failed to delete customer due to invalid close_date format.")
                return jsonify({"error": error_message}), 400

        query = session.query(HeavyMachineryOpportunity)
        if opportunity_id:
            query = query.filter(HeavyMachineryOpportunity.opportunity_id == opportunity_id)
        if account_name:
            query = query.filter(HeavyMachineryOpportunity.account_name == account_name)
        if dealer_id:
            query = query.filter(HeavyMachineryOpportunity.dealer_id == dealer_id)
        if dealer_code:
            query = query.filter(HeavyMachineryOpportunity.dealer_code == dealer_code)
        if opportunity_name:
            query = query.filter(HeavyMachineryOpportunity.opportunity_name == opportunity_name)
        if stage:
            query = query.filter(HeavyMachineryOpportunity.stage == stage)
        if probability is not None:
            query = query.filter(HeavyMachineryOpportunity.probability == probability)
        if close_date:
            query = query.filter(HeavyMachineryOpportunity.close_date == close_date)

        customers_to_delete = query.all()

        if not customers_to_delete:
            error_message = "Customer(s) not found based on provided query parameters."
            log_error(error_message)
            notify_failure("Customer Deletion Failed", "Failed to delete customer(s). No matching customer(s) found.")
            return jsonify({"error": error_message}), 404

        deleted_customers_info = []
        for customer in customers_to_delete:
            deleted_customers_info.append({
                "opportunity_id": customer.opportunity_id,
                "opportunity_name": customer.opportunity_name,
                "account_name": customer.account_name,
                "dealer_id": customer.dealer_id,
                "dealer_code": customer.dealer_code,
                "amount": customer.amount,
                "close_date": customer.close_date.strftime('%Y-%m-%d %H:%M:%S') if customer.close_date else None,
                "created_date": customer.created_date.strftime('%Y-%m-%d %H:%M:%S'),
                "employee_id": str(customer.employee_id) if customer.employee_id else None,
                "employee_name": f"{customer.employee.emp_first_name} {customer.employee.emp_last_name}" if customer.employee else None,
                "employee_num": customer.employee.emp_num if customer.employee else None,
                "product_id": str(customer.product_id) if customer.product_id else None,
                "product_name": customer.product_name,
                "product_brand": customer.product_brand,
                "product_model": customer.product_model,
            })
            session.delete(customer)

        session.commit()

        success_message = construct_success_message(deleted_customers_info)
        log_debug(f"Success message constructed for deleted customers.{success_message}")

        return jsonify({"message": "Deleted successfully", "details": deleted_customers_info}), 200

    except Exception as e:
        session.rollback()
        error_message = f"Error in deleting customer: {str(e)}"
        log_error(error_message)
        notify_failure("Customer Deletion Failed",
                       f"Failed to delete customer due to an internal server error.\nDetails: {str(e)}")
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    finally:
        session.close()
        log_info("End of delete_customer function")


if __name__ == "__main__":
    log_info(f"Starting the Flask application {app}.")
    app.run(debug=True)
    log_info("Flask application has stopped.")
