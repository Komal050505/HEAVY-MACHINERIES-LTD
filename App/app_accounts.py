from datetime import datetime

import pytz
from flask import Flask, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from Db_connections.configurations import session
from Logging_package.logging_utility import log_info, log_debug, log_error
from User_models.tables import Account, OTPStore
from Utilities.reusables import otp_required
from email_setup.email_operations import notify_success, notify_failure

app = Flask(__name__)


@app.route('/add-account', methods=['POST'])
@otp_required  # Applies the OTP decorator
def add_account():
    """
    Adds new accounts to the account table after OTP verification.
    """
    log_info("Received request to add new account")
    try:
        payload = request.get_json()
        log_debug(f"Request payload: {payload}")

        if not payload or 'account_id' not in payload or 'account_name' not in payload:
            error_message = "Invalid input data. 'account_id' and 'account_name' are required."
            log_error(error_message)
            return jsonify({"error": error_message}), 400

        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_time_ist = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S")

        new_account = Account(
            account_id=payload['account_id'],
            account_name=payload['account_name']
        )

        session.add(new_account)
        session.commit()
        log_info(f"Account added successfully: {payload['account_id']}")

        success_message = (f"Account added successfully.\nAccount ID: {payload['account_id']}\n"
                           f"Account Name: {payload['account_name']}\n"
                           f"Timestamp (IST): {current_time_ist}")
        notify_success("Add Account Successful", success_message)

        otp_record = session.query(OTPStore).filter_by(email=payload['email']).first()
        if otp_record:
            session.delete(otp_record)
            session.commit()
            log_info(f"OTP cleared for {payload['email']} after successful account addition.")

        return jsonify({
            "message": "Account added successfully",
            "account_id": payload['account_id'],
            "account_name": payload['account_name'],
            "timestamp": current_time_ist
        }), 201

    except SQLAlchemyError as e:
        session.rollback()
        error_message = f"Database error while adding account: {str(e)}"
        log_error(error_message)
        notify_failure("Add Account Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    except Exception as e:
        session.rollback()
        error_message = f"Unexpected error: {str(e)}"
        log_error(error_message)
        notify_failure("Add Account Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    finally:
        session.close()
        log_info("End of add_account function")


@app.route('/get-all-accounts', methods=['GET'])
def get_all_accounts():
    """
    Fetches all accounts from the account table.
    :return: JSON response with account details and total count, and sends an email notification.
    """
    log_info("Received request to get all accounts")
    try:
        accounts = session.query(Account).all()
        total_count = len(accounts)
        log_info(f"Fetched {total_count} accounts")

        accounts_list = []
        for account in accounts:
            account_dict = account.account_serialize_to_dict()

            if isinstance(account_dict.get('currency_conversions'), str):
                currency_conversions = {}
                conversions = account_dict['currency_conversions'].strip().split('\n')
                for conversion in conversions:
                    if conversion:
                        currency, value = conversion.split(': ', 1)
                        currency_conversions[currency] = value
                account_dict['currency_conversions'] = currency_conversions

            accounts_list.append(account_dict)

        account_details = "\n".join(
            [f"Account ID: {account['account_id']}\n"
             f"Account Name: {account['account_name']}\n"
             f"Currency Conversions:\n" +
             "\n".join(
                 [f"{currency}: {value}" for currency, value in account.get('currency_conversions', {}).items()]) + "\n"
             for account in accounts_list]
        )

        success_message = (
            f"Successfully retrieved Total {total_count} accounts.\n\n"
            f"Account Details:\n*********************************************\n{account_details}\n"
            f"\nTotal count of accounts: {total_count}"
        )

        notify_success("Get All Accounts Successful", success_message)

        return jsonify({"Accounts": accounts_list, "Total count of accounts": total_count}), 200

    except Exception as e:
        session.rollback()
        error_message = f"Error in fetching accounts: {str(e)}"
        log_error(error_message)
        notify_failure("Get Accounts Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500
    finally:
        session.close()
        log_info("End of get_all_accounts function")


@app.route('/get-single-account', methods=['GET'])
def get_single_account():
    """
    Fetched single account details
    :return: JSON response with email notifications
    """
    log_info(f"Received request to get account details with account id {'account_id'}")
    try:
        accountid = request.args.get('account_id')
        log_debug(f"Account ID fetched is: {accountid}")

        if not accountid:
            error_message = "Account ID not provided or invalid. Please provide a valid Account ID."
            log_error(error_message)
            notify_failure("Get Single Account Failed", error_message)
            return jsonify({"error": error_message}), 400

        account = session.query(Account).filter_by(account_id=accountid).first()

        if not account:
            error_message = f"Account not found: {accountid}"
            log_error(error_message)
            notify_failure("Get Single Account Failed", error_message)
            return jsonify({"error": "Account not found"}), 404

        log_info(f"Fetched account: {accountid}")

        account_details = account.account_serialize_to_dict()

        success_message = (f"Successfully fetched single account details - "
                           f"\n\nAccount ID: {account_details['account_id']}, "
                           f"\nName: {account_details['account_name']}")

        notify_success("Get Single Account Success", success_message)

        return jsonify({"Account": account_details, "Message": "Single Account Details:"}), 200

    except Exception as e:
        session.rollback()
        error_message = f"Error in fetching account: {str(e)}"
        log_error(error_message)
        notify_failure("Get Single Account Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    finally:
        session.close()
        log_info("End of get_single_account function")


@app.route('/update-account', methods=['PUT'])
@otp_required  # Apply the OTP decorator
def update_account():
    """
    Updates account name
    :return: JSON response with email notifications
    """
    log_info("Received request to update account details")
    try:
        data = request.get_json()
        account_id = data.get('account_id')
        new_account_name = data.get('account_name')

        log_debug(f"Account ID to update: {account_id}, New Name: {new_account_name}")

        if not account_id or not new_account_name:
            error_message = "Account ID and new Account Name must be provided."
            log_error(error_message)
            notify_failure("Update Account Failed", error_message)
            return jsonify({"error": error_message}), 400

        account = session.query(Account).filter_by(account_id=account_id).first()

        if not account:
            error_message = f"Account not found: {account_id}"
            log_error(error_message)
            notify_failure("Update Account Failed", error_message)
            return jsonify({"error": "Account not found"}), 404

        account.account_name = new_account_name
        session.commit()

        success_message = (f"Account ID: \n{account_id}\n\n"
                           f"Successfully updated with new name: \n{new_account_name}")
        log_info(success_message)
        notify_success("Update Account Success", success_message)

        return jsonify({
            "message": "Account details updated successfully.",
            "account_id": account_id,
            "new_account_name": new_account_name
        }), 200

    except Exception as e:
        session.rollback()
        error_message = f"Error in updating account: {str(e)}"
        log_error(error_message)
        notify_failure("Update Account Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    finally:
        session.close()
        log_info("End of update_account function")


@app.route('/delete-account', methods=['DELETE'])
@otp_required  # Apply the OTP decorator
def delete_account():
    """
    Deletes account based on account id
    :return: JSON response with email notifications
    """
    log_info("Received request to delete account")
    try:
        otp = request.args.get('otp')
        email = request.args.get('email')

        if not otp or not email:
            error_message = "OTP and email are required as query parameters."
            log_error(error_message)
            return jsonify({"error": error_message}), 400

        log_debug(f"Received OTP: {otp}, Email: {email}")

        account_id = request.args.get('account_id')
        log_debug(f"Account ID to delete: {account_id}")

        if not account_id:
            error_message = "Account ID must be provided."
            log_error(error_message)
            notify_failure("Delete Account Failed", error_message)
            return jsonify({"error": error_message}), 400

        account = session.query(Account).filter_by(account_id=account_id).first()

        if not account:
            error_message = f"Account not found: {account_id}"
            log_error(error_message)
            notify_failure("Delete Account Failed", error_message)
            return jsonify({"error": "Account not found"}), 404

        session.delete(account)
        session.commit()

        success_message = (f"Account ID: {account_id}\n"
                           f"Successfully account deleted. Details:\n"
                           f"Account ID: {account.account_id}\n"
                           f"Account Name: {account.account_name}")
        log_info(success_message)
        notify_success("Delete Account Success", success_message)

        return jsonify({
            "message": "Account successfully deleted.",
            "deleted_account_id": account_id,
            "account_name": account.account_name
        }), 200

    except Exception as e:
        session.rollback()
        error_message = f"Error in deleting account: {str(e)}"
        log_error(error_message)
        notify_failure("Delete Account Failed", error_message)
        return jsonify({"error": "Internal server error", "details": error_message}), 500

    finally:
        session.close()
        log_info("End of delete_account function")


if __name__ == "__main__":
    log_info(f"Starting the Flask application {app}.")
    app.run(debug=True)
    log_info("Flask application has stopped.")
