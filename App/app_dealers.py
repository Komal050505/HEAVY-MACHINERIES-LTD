from flask import jsonify, Flask, request
from sqlalchemy.exc import SQLAlchemyError

from Db_connections.configurations import session
from Logging_package.logging_utility import log_info, log_debug, log_error
from User_models.tables import HeavyMachineriesDealer
from Utilities.reusables import otp_required
from email_setup.email_operations import notify_failure, notify_success

app = Flask(__name__)


@app.route('/add-dealer', methods=['POST'])
@otp_required  # Apply the OTP decorator
def add_dealer():
    """
    Adds new Dealer to the dealer table
    :return: JSON response with email notifications
    """
    log_info("Received request to add new dealer")
    try:
        payload = request.get_json()
        log_debug(f"Request payload: {payload}")

        if not payload or 'dealer_code' not in payload or 'opportunity_owner' not in payload:
            error_message = "Invalid input data. 'dealer_code' and 'opportunity_owner' are required."
            log_error(error_message)
            notify_failure("Add Dealer Failed", error_message)
            return jsonify({"error": error_message}), 400

        new_dealer = HeavyMachineriesDealer(
            dealer_code=payload['dealer_code'],
            opportunity_owner=payload['opportunity_owner']
        )

        session.add(new_dealer)
        session.commit()
        log_info(f"Dealer added successfully: {new_dealer.dealer_id}")

        success_message = (f"Dealer added successfully.\n\n"
                           f"Dealer ID: {new_dealer.dealer_id}\n\n"
                           f"Dealer Code: {payload['dealer_code']}\n\n"
                           f"Opportunity Owner: {payload['opportunity_owner']}")
        notify_success("Add Dealer Successful", success_message)

        return jsonify({
            "message": "Dealer added successfully",
            "dealer_id": new_dealer.dealer_id,
            "dealer_code": payload['dealer_code'],
            "opportunity_owner": payload['opportunity_owner']
        }), 201

    except SQLAlchemyError as e:
        session.rollback()
        error_message = f"Error inserting dealer: {str(e)}"
        log_error(error_message)
        notify_failure("Add Dealer Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    except Exception as e:
        session.rollback()
        error_message = f"Unexpected error: {str(e)}"
        log_error(error_message)
        notify_failure("Add Dealer Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    finally:
        session.close()
        log_info("End of add_dealer function")


@app.route('/get-all-dealers', methods=['GET'])
def get_all_dealers():
    """
    Fetches all dealers data
    :return: JSON Response with emil notifications
    """
    log_info("Received request to get all dealers")
    try:
        dealers = session.query(HeavyMachineriesDealer).all()

        if not dealers:
            log_info("No dealers found.")
            return jsonify({"message": "No dealers found"}), 404

        dealers_data = [dealer.dealer_serialize_to_dict() for dealer in dealers]

        success_message = f"Dealers retrieved successfully. Count: {len(dealers)}"
        log_info(success_message)
        notify_success("Get All Dealers Successful", success_message)

        return jsonify({
            "message": "Dealers retrieved successfully.",
            "Total count": len(dealers),
            "dealers": dealers_data
        }), 200

    except SQLAlchemyError as e:
        session.rollback()
        error_message = f"Error retrieving dealers: {str(e)}"
        log_error(error_message)
        notify_failure("Get All Dealers Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    except Exception as e:
        session.rollback()
        error_message = f"Unexpected error: {str(e)}"
        log_error(error_message)
        notify_failure("Get All Dealers Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    finally:
        session.close()
        log_info("End of get_all_dealers function")


@app.route('/get-particular-dealers', methods=['GET'])
def get_particular_dealers():
    """
    Fetches particular dealers based on dealer id, dealer code, opportunity owner
    :return: JSON response with email notifications
    """
    log_info("Received request to get particular dealers by parameters")
    try:
        dealer_id = request.args.get('dealer_id')
        dealer_code = request.args.get('dealer_code')
        opportunity_owner = request.args.get('opportunity_owner')

        log_debug(
            f"Search parameters - dealer_id: {dealer_id}, dealer_code: {dealer_code}, "
            f"opportunity_owner: {opportunity_owner}")

        if not dealer_id and not dealer_code and not opportunity_owner:
            error_message = "At least one of 'dealer_id', 'dealer_code', or 'opportunity_owner' must be provided."
            log_error(error_message)
            notify_failure("Get Dealers Failed", error_message)
            return jsonify({"error": error_message}), 400

        query = session.query(HeavyMachineriesDealer)

        if dealer_id:
            query = query.filter_by(dealer_id=dealer_id)
        if dealer_code:
            query = query.filter_by(dealer_code=dealer_code)
        if opportunity_owner:
            query = query.filter_by(opportunity_owner=opportunity_owner)

        dealers = query.all()

        if not dealers:
            error_message = "No dealers found with the provided parameters."
            log_info(error_message)
            notify_success("Get Dealers", error_message)
            return jsonify({"message": error_message}), 404

        dealers_data = [dealer.dealer_serialize_to_dict() for dealer in dealers]

        formatted_dealers_info = "\n".join([
            f"Dealer ID: {dealer['dealer_id']}\n"
            f"Dealer Code: {dealer['dealer_code']}\n"
            f"Opportunity Owner: {dealer['opportunity_owner']}\n"
            "-------------------------"
            for dealer in dealers_data
        ])
        success_message = (f"Retrieved {len(dealers)} dealer(s) successfully.\n\n"
                           f"Dealer Details:\n{formatted_dealers_info}")
        log_info(success_message)
        notify_success("Get Dealers Successful", success_message)

        return jsonify({
            "message": f"Retrieved Total {len(dealers)} dealer(s) successfully.",
            "dealers": dealers_data
        }), 200

    except SQLAlchemyError as e:
        session.rollback()
        error_message = f"Error retrieving dealers: {str(e)}"
        log_error(error_message)
        notify_failure("Get Dealers Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    except Exception as e:
        session.rollback()
        error_message = f"Unexpected error: {str(e)}"
        log_error(error_message)
        notify_failure("Get Dealers Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    finally:
        session.close()
        log_info("End of get_dealers function")


@app.route('/update-dealer', methods=['PUT'])
@otp_required  # Apply the OTP decorator
def update_dealer():
    """
    Updates dealer based on dealer id
    :return: JSON response with email notifications
    """
    log_info("Received request to update a dealer")
    try:
        data = request.json
        dealer_id = data.get('dealer_id')
        dealer_code = data.get('dealer_code')
        opportunity_owner = data.get('opportunity_owner')

        log_debug(
            f"Data received for update: dealer_id={dealer_id}, dealer_code={dealer_code}, "
            f"opportunity_owner={opportunity_owner}")

        if not dealer_id:
            error_message = "Dealer ID must be provided to update a dealer."
            log_error(error_message)
            notify_failure("Update Dealer Failed", error_message)
            return jsonify({"error": error_message}), 400

        dealer = session.query(HeavyMachineriesDealer).filter_by(dealer_id=dealer_id).first()

        if not dealer:
            error_message = f"No dealer found with dealer_id: {dealer_id}"
            log_error(error_message)
            notify_failure("Update Dealer Failed", error_message)
            return jsonify({"error": "Dealer not found"}), 404

        if dealer_code:
            dealer.dealer_code = dealer_code
        if opportunity_owner:
            dealer.opportunity_owner = opportunity_owner

        session.commit()

        updated_dealer_data = dealer.dealer_serialize_to_dict()

        success_message = (f"Dealer updated successfully.\n\n"
                           f"Updated Dealer ID: {updated_dealer_data['dealer_id']}\n"
                           f"Updated Dealer Code: {updated_dealer_data['dealer_code']}\n"
                           f"Updated Opportunity Owner: {updated_dealer_data['opportunity_owner']}")
        log_info(success_message)
        notify_success("Dealer Updated Successfully", success_message)

        return jsonify({
            "message": "Dealer updated successfully.",
            "dealer": updated_dealer_data
        }), 200

    except SQLAlchemyError as e:
        session.rollback()
        error_message = f"Error updating dealer: {str(e)}"
        log_error(error_message)
        notify_failure("Update Dealer Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    except Exception as e:
        session.rollback()
        error_message = f"Unexpected error: {str(e)}"
        log_error(error_message)
        notify_failure("Update Dealer Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    finally:
        session.close()
        log_info("End of update_dealer function")


@app.route('/delete-single-dealer', methods=['DELETE'])
@otp_required  # Apply the OTP decorator
def delete_single_dealer():
    """
    Deletes a single dealer based on dealer_id, dealer_code, or opportunity_owner.
    OTP and email are provided as query parameters.
    :return: JSON response with email notifications
    """
    log_info("Received request to delete a dealer")
    try:
        otp = request.args.get('otp')
        email = request.args.get('email')

        if not otp or not email:
            error_message = "OTP and email are required as query parameters."
            log_error(error_message)
            return jsonify({"error": error_message}), 400

        log_debug(f"Received OTP: {otp}, Email: {email}")

        dealer_id = request.args.get('dealer_id')
        dealer_code = request.args.get('dealer_code')
        opportunity_owner = request.args.get('opportunity_owner')
        log_debug(f"Dealer ID: {dealer_id}, Dealer Code: {dealer_code}, Opportunity Owner: {opportunity_owner}")

        if not dealer_id and not dealer_code and not opportunity_owner:
            error_message = "At least one of 'dealer_id', 'dealer_code', or 'opportunity_owner' must be provided."
            log_error(error_message)
            notify_failure("Delete Dealer Failed", error_message)
            return jsonify({"error": error_message}), 400

        query = session.query(HeavyMachineriesDealer)
        if dealer_id:
            query = query.filter_by(dealer_id=dealer_id)
        if dealer_code:
            query = query.filter_by(dealer_code=dealer_code)
        if opportunity_owner:
            query = query.filter_by(opportunity_owner=opportunity_owner)

        dealers_to_delete = query.first()

        if not dealers_to_delete:
            error_message = "Dealer not found with the given criteria."
            log_error(error_message)
            notify_failure("Delete Dealer Failed", error_message)
            return jsonify({"error": error_message}), 404

        for dealer in dealers_to_delete:
            session.delete(dealer)

        session.commit()
        success_message = f"Deleted {len(dealers_to_delete)} dealer(s) successfully."
        log_info(success_message)
        notify_success("Delete Dealer Successful", success_message)

        return jsonify({"message": success_message}), 200

    except SQLAlchemyError as e:
        session.rollback()
        error_message = f"Error deleting dealer: {str(e)}"
        log_error(error_message)
        notify_failure("Delete Dealer Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    except Exception as e:
        session.rollback()
        error_message = f"Unexpected error: {str(e)}"
        log_error(error_message)
        notify_failure("Delete Dealer Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    finally:
        session.close()
        log_info("End of delete_dealer function")


@app.route('/delete-all-dealers', methods=['DELETE'])
@otp_required  # Apply the OTP decorator
def delete_all_dealers():
    """
    Deletes all dealers based on dealer id/ dealer code/ opportunity owner
    :return: JSON response with email notifications
    """
    log_info("Received request to delete dealers")
    try:
        dealer_id = request.args.get('dealer_id')
        dealer_code = request.args.get('dealer_code')
        opportunity_owner = request.args.get('opportunity_owner')

        if not dealer_id and not dealer_code and not opportunity_owner:
            error_message = "At least one of 'dealer_id', 'dealer_code', or 'opportunity_owner' must be provided."
            log_error(error_message)
            return jsonify({"error": error_message}), 400

        query = session.query(HeavyMachineriesDealer)

        if dealer_id:
            query = query.filter(HeavyMachineriesDealer.dealer_id == dealer_id)
        if dealer_code:
            query = query.filter(HeavyMachineriesDealer.dealer_code == dealer_code)
        if opportunity_owner:
            query = query.filter(HeavyMachineriesDealer.opportunity_owner == opportunity_owner)

        dealers_to_delete = query.all()

        if not dealers_to_delete:
            error_message = "No dealers found with the given criteria."
            log_error(error_message)
            return jsonify({"error": error_message}), 404

        for dealer in dealers_to_delete:
            session.delete(dealer)
        session.commit()

        success_message = f"Deleted {len(dealers_to_delete)} dealer(s) successfully."
        log_info(success_message)
        notify_success("Delete Dealers Successful", success_message)

        return jsonify({"message": success_message}), 200

    except SQLAlchemyError as e:
        session.rollback()
        error_message = f"Error deleting dealers: {str(e)}"
        log_error(error_message)
        notify_failure("Delete Dealers Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    except Exception as e:
        session.rollback()
        error_message = f"Unexpected error: {str(e)}"
        log_error(error_message)
        notify_failure("Delete Dealers Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    finally:
        session.close()
        log_info("End of delete_dealers function")


if __name__ == "__main__":
    log_info(f"Starting the Flask application {app}.")
    app.run(debug=True)
    log_info("Flask application has stopped.")
