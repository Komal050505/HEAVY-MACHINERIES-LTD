import traceback
import uuid
from datetime import datetime

import pytz
from flask import jsonify, request, Flask
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.http import parse_date

from Db_connections.configurations import session
from Logging_package.logging_utility import log_info, log_error, log_debug
from User_models.tables import HeavyMachineryOpportunity, Account, HeavyMachineriesDealer, Employee, HeavyProduct
from Utilities.reusables import otp_required, get_opportunity_stage, get_currency_conversion, validate_probability, \
    validate_stage, validate_positive_number
from email_setup.email_operations import notify_failure, notify_success, notify_opportunity_update_success, \
    notify_opportunity_details

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
            employee = session.query(Employee).filter_by(id=employee_id).first()  # Make sure 'id' is UUID
            if not employee:
                error_message = f"Employee with ID {employee_id} not found."
                log_error(error_message)
                notify_failure("Customer Creation Failed", error_message)
                return jsonify({"error": error_message}), 404
            else:
                log_info(f"Employee found: {employee.first_name} {employee.last_name}, ID: {employee.emp_num}")
        else:
            error_message = "Employee ID is required."
            log_error(error_message)
            notify_failure("Customer Creation Failed", error_message)
            return jsonify({"error": error_message}), 400

        product_id = payload.get("product_id")
        if product_id:
            product = session.query(HeavyProduct).filter_by(id=product_id).first()
            if product:
                log_info(f"Product found: {product.name}")
                payload.update({
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "product_brand": product.brand,
                    "product_model": product.model,
                    "product_image_url": product.image_url
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
        # Retrieve query parameters
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

        # New parameters for employee and product
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

        # Parse dates if provided
        if created_date_start:
            created_date_start = datetime.fromisoformat(created_date_start.replace('Z', '+00:00'))
            log_info(f"Parsed created_date_start: {created_date_start}")

        if close_date_end:
            close_date_end = datetime.fromisoformat(close_date_end.replace('Z', '+00:00'))
            log_info(f"Parsed close_date_end: {close_date_end}")

        # Validate probabilities
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

        # Construct the query
        query = session.query(HeavyMachineryOpportunity)
        log_info("Constructed initial query")

        # Apply filters based on provided parameters
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

        # New filters for employee and product
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

        # Execute the query and fetch results
        opportunities = query.all()
        total_count = len(opportunities)
        log_info(f"Fetched {total_count} opportunities based on query parameters")

        # Serialize the results
        opportunities_list = [opportunity.serialize_to_dict() for opportunity in opportunities]
        log_info("Serialized opportunities to dictionary format")

        # Notify with detailed opportunity information
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
        log_error(git traceback.format_exc())
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


@app.route('/update-opportunity', methods=['PUT'])
@otp_required  # Apply the OTP decorator
def update_opportunity():
    """
    Update an existing Opportunity record.
    :return: JSON response indicating success or failure.
    """
    log_info("Received request to update opportunity")

    try:
        data = request.get_json()
        log_info(f"Request data: {data}")

        opportunity_id = data.get('opportunity_id')
        opportunity_name = data.get('opportunity_name')
        account_name = data.get('account_name')
        close_date = data.get('close_date')
        amount = data.get('amount')
        description = data.get('description')
        dealer_id = data.get('dealer_id')
        dealer_code = data.get('dealer_code')
        stage = data.get('stage')
        probability = data.get('probability')
        next_step = data.get('next_step')
        amount_in_words = data.get('amount_in_words')
        currency_conversions = data.get('currency_conversions', {})
        vehicle_model = data.get('vehicle_model')
        vehicle_year = data.get('vehicle_year')
        vehicle_color = data.get('vehicle_color')
        vehicle_model_id = data.get('vehicle_model_id')
        log_info(f"Extracted fields: opportunity_id={opportunity_id}, opportunity_name={opportunity_name}, "
                 f"account_name={account_name}, close_date={close_date}, amount={amount}, description={description}, "
                 f"dealer_id={dealer_id}, dealer_code={dealer_code}, stage={stage}, probability={probability}, "
                 f"next_step={next_step}, amount_in_words={amount_in_words}, currency_conversions={currency_conversions}, "
                 f"vehicle_model={vehicle_model}, vehicle_year={vehicle_year}, vehicle_color={vehicle_color},"
                 f"vehicle_model_id={vehicle_model_id}")
        if not opportunity_id:
            raise ValueError("Opportunity ID is required.")
        log_info("Opportunity ID provided.")

        if opportunity_name and len(opportunity_name) > 255:
            raise ValueError("Opportunity name is too long. Maximum length is 255 characters.")

        if account_name and len(account_name) > 255:
            raise ValueError("Account name is too long. Maximum length is 255 characters.")
        log_info("Validated length of opportunity_name and account_name.")

        if close_date:
            close_date = parse_date(close_date)
            log_info(f"Parsed close_date: {close_date}")

        if amount is not None and not validate_positive_number(amount):
            raise ValueError("Amount must be a positive number.")

        if probability is not None and not validate_probability(probability):
            raise ValueError("Probability must be between 0 and 100.")

        if stage:
            stage = validate_stage(stage)
            log_info(f"Validated stage: {stage}")

        valid_currencies = ['usd', 'aus', 'cad', 'jpy', 'eur', 'gbp', 'cny']

        for currency in valid_currencies:
            if currency in currency_conversions:
                if not validate_positive_number(currency_conversions[currency]):
                    raise ValueError(f"Invalid value for currency conversion {currency}. Must be a positive number.")
        log_info("Validated currency conversions.")

        if vehicle_model_id and not isinstance(vehicle_model_id, int):
            raise ValueError("Vehicle model ID must be an integer.")

        opportunity = session.query(HeavyMachineryOpportunity).filter_by(opportunity_id=opportunity_id).first()

        if not opportunity:
            raise ValueError("Opportunity not found.")
        log_info(f"Found opportunity with ID {opportunity_id}.")

        updated_fields = {}

        if opportunity_name:
            opportunity.opportunity_name = opportunity_name
            updated_fields['opportunity_name'] = opportunity_name

        if account_name:
            opportunity.account_name = account_name
            updated_fields['account_name'] = account_name

        if close_date:
            opportunity.close_date = close_date
            updated_fields['close_date'] = close_date

        if amount is not None:
            opportunity.amount = amount
            conversions = get_currency_conversion(amount)
            opportunity.usd = conversions.get('USD')
            opportunity.aus = conversions.get('AUD')
            opportunity.cad = conversions.get('CAD')
            opportunity.jpy = conversions.get('JPY')
            opportunity.eur = conversions.get('EUR')
            opportunity.gbp = conversions.get('GBP')
            opportunity.cny = conversions.get('CNY')
            updated_fields['amount'] = amount
            updated_fields['currency_conversions'] = conversions

        if description:
            opportunity.description = description
            updated_fields['description'] = description

        if dealer_id:
            opportunity.dealer_id = dealer_id
            updated_fields['dealer_id'] = dealer_id

        if dealer_code:
            opportunity.dealer_code = dealer_code
            updated_fields['dealer_code'] = dealer_code

        if stage:
            opportunity.stage = stage
            updated_fields['stage'] = stage

        if probability is not None:
            opportunity.probability = probability
            updated_fields['probability'] = probability

        if next_step:
            opportunity.next_step = next_step
            updated_fields['next_step'] = next_step

        if amount_in_words:
            opportunity.amount_in_words = amount_in_words
            updated_fields['amount_in_words'] = amount_in_words

        if vehicle_model:
            opportunity.vehicle_model = vehicle_model
            updated_fields['vehicle_model'] = vehicle_model

        if vehicle_year:
            if not isinstance(vehicle_year, int) or vehicle_year < 1900 or vehicle_year > datetime.now().year:
                raise ValueError("Vehicle year must be a valid year.")
            opportunity.vehicle_year = vehicle_year
            updated_fields['vehicle_year'] = vehicle_year

        if vehicle_color:
            opportunity.vehicle_color = vehicle_color
            updated_fields['vehicle_color'] = vehicle_color

        if vehicle_model_id:
            opportunity.vehicle_model_id = vehicle_model_id
            updated_fields['vehicle_model_id'] = vehicle_model_id

        if currency_conversions:
            opportunity.usd = currency_conversions.get('usd')
            opportunity.aus = currency_conversions.get('aus')
            opportunity.cad = currency_conversions.get('cad')
            opportunity.jpy = currency_conversions.get('jpy')
            opportunity.eur = currency_conversions.get('eur')
            opportunity.gbp = currency_conversions.get('gbp')
            opportunity.cny = currency_conversions.get('cny')
            updated_fields['currency_conversions'] = currency_conversions

        log_info(f"Updating fields: {updated_fields}")
        session.commit()
        log_info(f"Opportunity with ID {opportunity_id} updated successfully.")

        notify_opportunity_update_success(
            "Update Opportunity Successful",
            {"opportunity_id": opportunity_id, "updated_fields": updated_fields}
        )

        return jsonify({
            "message": "Opportunity updated successfully.",
            "opportunity_id": opportunity_id,
            "updated_fields": updated_fields
        }), 200

    except ValueError as ve:
        session.rollback()
        error_message = f"Validation error: {str(ve)}"
        log_error(error_message)
        notify_failure("Update Opportunity Validation Failed", error_message)
        return jsonify({"error": "Bad Request", "details": error_message}), 400

    except SQLAlchemyError as sae:
        session.rollback()
        error_message = f"Database error: {str(sae)}"
        log_error(error_message)
        notify_failure("Update Opportunity Database Error", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    except Exception as e:
        session.rollback()
        error_message = f"Error updating opportunity: {str(e)}"
        log_error(error_message)
        notify_failure("Update Opportunity Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    finally:
        session.close()
        log_info("End of update_opportunity function")


@app.route('/delete-customer', methods=["DELETE"])
@otp_required  # Apply the OTP decorator
def delete_customer():
    """
    Deletes a customer from the opportunity table based on query parameters.
    :return: JSON response with email notifications and result of deletion.
    """
    log_info("Received request to delete customer")
    try:
        otp = request.args.get('otp')
        email = request.args.get('email')

        if not otp or not email:
            error_message = "OTP and email are required as query parameters."
            log_error(error_message)
            return jsonify({"error": error_message}), 400

        log_debug(f"Received OTP: {otp}, Email: {email}")

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
            detailed_error_message = "Failed to delete customer due to missing query parameters."
            notify_failure("Customer Deletion Failed", detailed_error_message)
            return jsonify({"error": error_message}), 400

        if close_date:
            try:
                close_date = datetime.strptime(close_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                error_message = "Invalid close_date format. Use 'YYYY-MM-DD HH:MM:SS'."
                log_error(error_message)
                detailed_error_message = "Failed to delete customer due to invalid close_date format."
                notify_failure("Customer Deletion Failed", detailed_error_message)
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
            detailed_error_message = "Failed to delete customer(s). No matching customer(s) found."
            notify_failure("Customer Deletion Failed", detailed_error_message)
            return jsonify({"error": error_message}), 404

        for customer in customers_to_delete:
            session.delete(customer)

        session.commit()

        success_message = (
                f"Customer(s) deleted successfully.\n\n\n"
                f"Deleted Customers:\n" + "\n".join([f"Opportunity ID: {customer.opportunity_id}\n"
                                                     f"Opportunity Name: {customer.opportunity_name}\n"
                                                     f"Account Name: {customer.account_name}\n"
                                                     f"Dealer ID: {customer.dealer_id}\n"
                                                     f"Dealer Code: {customer.dealer_code}\n"
                                                     f"Amount: {customer.amount}\n"
                                                     f"Close Date: {customer.close_date.strftime('%Y-%m-%d %H:%M:%S') if customer.close_date else None}\n"
                                                     f"Created Date: {customer.created_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                                     for customer in customers_to_delete])

        )
        notify_success("Customer Deletion Successful", success_message)

        return jsonify({"message": "Deleted successfully"}), 200

    except Exception as e:
        session.rollback()
        error_message = f"Error in deleting customer: {str(e)}"
        log_error(error_message)
        detailed_error_message = f"Failed to delete customer due to an internal server error.\nDetails: {str(e)}"
        notify_failure("Customer Deletion Failed", detailed_error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    finally:
        session.close()
        log_info("End of delete_customer function")


if __name__ == "__main__":
    log_info(f"Starting the Flask application {app}.")
    app.run(debug=True)
    log_info("Flask application has stopped.")
