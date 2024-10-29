"""
Email Setup and Notification Module

This module provides functions to set up email configurations and send email notifications.

Functions:
    send_email(too_email, subject, body): Sends an email to the specified recipients.
    notify_success(subject, body): Sends a success notification email.
    notify_failure(subject, body): Sends a failure notification email.
"""

# Standard library imports (for sending emails)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from Db_connections.configurations import session
from Logging_package.logging_utility import log_info, log_error, log_debug, log_warning
# Application-specific imports from our application(for email configuration details)
from email_setup.email_config import (
    SENDER_EMAIL,
    PASSWORD,
    SMTP_SERVER,
    SMTP_PORT, ERROR_HANDLING_GROUP_EMAIL, RECEIVER_EMAIL
)


def send_email_otp(receiver_email, otp):
    """Send OTP to the user's email."""
    sender_email = SENDER_EMAIL
    sender_password = PASSWORD
    subject = "Your OTP"
    body = f"Your OTP is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


def send_email(too_email, subject, body):
    """
    This function is used to send emails whenever there are changes in CRUD operations
    :param too_email: list of email addresses needed to be sent
    :param subject: The subject of the email
    :param body: The message which user needs to be notified
    :return: None
    """
    if too_email is None:
        too_email = []

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(too_email)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, too_email, msg.as_string())


# -------------------------------------------- Employee table ----------------------------------------------------------

def generate_employee_email_body(employee):
    """
    Generates the email body for a newly added employee.

    :param employee: The Employee object containing employee details.
    :return: A string formatted as the email body.
    """
    email_body = f"""
    Dear {employee.emp_first_name} {employee.emp_last_name},

    Welcome to the team! We are excited to have you join us as a {employee.emp_position} in the {employee.emp_department} department.

    Here are your details:
    - **Employee Id:** {employee.emp_id}
    - **Full Name:** {employee.emp_first_name} {employee.emp_last_name}
    - **Email:** {employee.emp_email}
    - **Employee Number:** {employee.emp_num}
    - **Phone:** {employee.emp_phone}
    - **Hire Date:** {employee.emp_hire_date.strftime('%Y-%m-%d')}
    - **Position:** {employee.emp_position}
    - **Salary:** ${employee.emp_salary:,.2f}
    - **Age:** {employee.emp_age}
    - **Sex:** {employee.emp_sex}
    - **Blood Group:** {employee.emp_blood_group}
    - **Height:** {employee.emp_height} cm
    - **Weight:** {employee.emp_weight} kg
    - **Address:** {employee.emp_address}
    - **Emergency Contact:** {employee.emp_emergency_contact}
    - **Nationality:** {employee.emp_nationality}
    - **Date of Birth:** {employee.emp_date_of_birth.strftime('%Y-%m-%d')}
    - **Marital Status:** {employee.emp_marital_status}
    - **Employment Status:** {employee.emp_employment_status}
    - **Insurance Number:** {employee.emp_insurance_number}
    - **Created At:** {employee.emp_created_at}

    Please keep this information safe. If you have any questions, feel free to reach out to the HR team.

    Best Regards,
    HR Team
    """

    return email_body


def generate_employee_notification_body(employee_list, total_count):
    """
    Generate an email body with the details of fetched employees.

    :param employee_list: List of employee dictionaries.
    :param total_count: Total number of employees fetched.
    :return: Formatted email body as a string.
    """
    body = f"Total Employees Fetched: {total_count}\n\n"
    body += "Employee Details:\n"

    for emp in employee_list:
        body += (
            f"*******************************\n"
            f"Employee Id: {emp['emp_id']}\n"
            f"Name: {emp['emp_first_name']} {emp['emp_last_name']}\n"
            f"Employee Number: {emp['emp_num']}\n"
            f"Email: {emp['emp_email']}\n"
            f"Phone: {emp['emp_phone']}\n"
            f"Position: {emp['emp_position']}\n"
            f"Department: {emp['emp_department']}\n"
            f"Salary: {emp['emp_salary']}\n"
            f"Age: {emp['emp_age']}\n"
            f"Sex: {emp['emp_sex']}\n"
            f"Blood Group: {emp['emp_blood_group']}\n"
            f"Height: {emp['emp_height']}\n"
            f"Weight: {emp['emp_weight']}\n"
            f"Address: {emp['emp_address']}\n"
            f"Emergency Contact: {emp['emp_emergency_contact']}\n"
            f"Nationality: {emp['emp_nationality']}\n"
            f"Date of Birth: {emp['emp_date_of_birth']}\n"
            f"Marital Status: {emp['emp_marital_status']}\n"
            f"Employment Status: {emp['emp_employment_status']}\n"
            f"Insurance Number: {emp['emp_insurance_number']}\n"
            f"\n"
        )

    return body


def generate_update_notification_body(updated_employee, update_time):
    """
    Generates an email body containing the updated employee details and timestamp of the update.

    Parameters:
    - updated_employee: Dictionary containing updated employee fields.
    - update_time: String timestamp of when the update occurred.

    Returns:
    - A formatted string to be used as the email body.
    """
    email_body = f"""
    Employee Update Notification

    The details of employee ID {updated_employee['emp_id']} were successfully updated on {update_time}.

    Updated Details:
    First Name: {updated_employee.get('emp_first_name', 'N/A')}
    Last Name: {updated_employee.get('emp_last_name', 'N/A')}
    Email: {updated_employee.get('emp_email', 'N/A')}
    Employee Number: {updated_employee.get('emp_num', 'N/A')}
    Phone: {updated_employee.get('emp_phone', 'N/A')}
    Position: {updated_employee.get('emp_position', 'N/A')}
    Salary: {updated_employee.get('emp_salary', 'N/A')}
    Department: {updated_employee.get('emp_department', 'N/A')}
    Hire Date: {updated_employee.get('emp_hire_date', 'N/A')}
    Age: {updated_employee.get('emp_age', 'N/A')}
    Sex: {updated_employee.get('emp_sex', 'N/A')}
    Blood Group: {updated_employee.get('emp_blood_group', 'N/A')}
    Height: {updated_employee.get('emp_height', 'N/A')}
    Weight: {updated_employee.get('emp_weight', 'N/A')}
    Address: {updated_employee.get('emp_address', 'N/A')}
    Emergency Contact: {updated_employee.get('emp_emergency_contact', 'N/A')}
    Nationality: {updated_employee.get('emp_nationality', 'N/A')}
    Date of Birth: {updated_employee.get('emp_date_of_birth', 'N/A')}
    Marital Status: {updated_employee.get('emp_marital_status', 'N/A')}
    Employment Status: {updated_employee.get('emp_employment_status', 'N/A')}
    Insurance Number: {updated_employee.get('emp_insurance_number', 'N/A')}

    Regards,
    HR System
    """
    return email_body


def generate_delete_notification(employee, deleted_time):
    """
    Generate an email body with the details of the deleted employee.

    :param employee: Employee object that was deleted.
    :param deleted_time: The time when the employee was deleted.
    :return: Formatted email body as a string.
    """
    body = f"Employee {employee.emp_first_name} {employee.emp_last_name} (ID: {employee.emp_id}) has been deleted from the system.\n\n"
    body += "Deleted Employee Details:\n"
    body += f"Employee Number: {employee.emp_num}\n"
    body += f"Email: {employee.emp_email}\n"
    body += f"Phone: {employee.emp_phone}\n"
    body += f"Position: {employee.emp_position}\n"
    body += f"Department: {employee.emp_department}\n"
    body += f"Hire Date: {employee.emp_hire_date}\n"
    body += f"Age: {employee.emp_age}\n"
    body += f"Sex: {employee.emp_sex}\n"
    body += f"Blood Group: {employee.emp_blood_group}\n"
    body += f"Height: {employee.emp_height}\n"
    body += f"Weight: {employee.emp_weight}\n"
    body += f"Address: {employee.emp_address}\n"
    body += f"Emergency Contact: {employee.emp_emergency_contact}\n"
    body += f"Nationality: {employee.emp_nationality}\n"
    body += f"Date of Birth: {employee.emp_date_of_birth}\n"
    body += f"Marital Status: {employee.emp_marital_status}\n"
    body += f"Employment Status: {employee.emp_employment_status}\n"
    body += f"Insurance Number: {employee.emp_insurance_number}\n"
    body += f"Created At: {employee.emp_created_at}\n"
    body += f"Deleted Time: {deleted_time}\n"

    return body


# ------------------------------------------------ Product table -------------------------------------------------------
def generate_heavy_product_email_body(product, employee):
    """
    Generates the email body for a newly added heavy product.

    :param product: The HeavyProduct object containing product details.
    :param employee: The Employee object containing employee details.
    :return: A string formatted as the email body.
    """
    email_body = f"""
    Dear Admin,

    A new heavy product has been added to the inventory. Here are the details:

    **Product Details:**
    - **Product ID:** {product.heavy_product_id}
    - **Name:** {product.heavy_product_name}
    - **Type:** {product.heavy_product_type}
    - **Brand:** {product.heavy_product_brand}
    - **Model:** {product.heavy_product_model}
    - **Year of Manufacture:** {product.heavy_product_year_of_manufacture}
    - **Price:** ${product.heavy_product_price:,.2f}
    - **Weight:** {product.heavy_product_weight} kg
    - **Dimensions:** {product.heavy_product_dimensions}
    - **Engine Type:** {product.heavy_product_engine_type}
    - **Horsepower:** {product.heavy_product_horsepower}
    - **Fuel Capacity:** {product.heavy_product_fuel_capacity} liters
    - **Operational Hours:** {product.heavy_product_operational_hours}
    - **Warranty Period:** {product.heavy_product_warranty_period} months
    - **Status:** {product.heavy_product_status}
    - **Description:** {product.heavy_product_description}
    - **Image URL:** {product.heavy_product_image_url}
    - **Created At:** {product.heavy_product_created_at.isoformat()}
    - **Updated At:** {product.heavy_product_updated_at.isoformat()}

    **Employee Details:**
    - **Employee ID:** {employee.emp_id}
    - **Name:** {employee.emp_first_name} {employee.emp_last_name}
    - **Employee Number:** {employee.emp_num}

    Please review the new product and update the inventory as necessary.

    Best Regards,
    Inventory Management System
    """

    return email_body


def generate_heavy_product_fetched_body(heavy_product_list, total_count):
    """
    Generate an email body with the details of fetched heavy products.

    :param heavy_product_list: List of heavy product dictionaries.
    :param total_count: Total number of heavy products fetched.
    :return: Formatted email body as a string.
    """
    body = f"Total Heavy Products Fetched: {total_count}\n\n"
    body += "Heavy Product Details:\n"

    for product in heavy_product_list:
        body += (
            f"*******************************\n"
            f"Product Id: {product['heavy_product_id']}\n"
            f"Name: {product['heavy_product_name']}\n"
            f"Product Type: {product['heavy_product_type']}\n"
            f"Brand: {product['heavy_product_brand']}\n"
            f"Model: {product['heavy_product_model']}\n"
            f"Year of Manufacture: {product['heavy_product_year_of_manufacture']}\n"
            f"Price: {product['heavy_product_price']}\n"
            f"Weight: {product['heavy_product_weight']} kg\n"
            f"Dimensions: {product['heavy_product_dimensions']}\n"
            f"Engine Type: {product['heavy_product_engine_type']}\n"
            f"Horsepower: {product['heavy_product_horsepower']} hp\n"
            f"Fuel Capacity: {product['heavy_product_fuel_capacity']} liters\n"
            f"Operational Hours: {product['heavy_product_operational_hours']}\n"
            f"Warranty Period: {product['heavy_product_warranty_period']} months\n"
            f"Status: {product['heavy_product_status']}\n"
            f"Description: {product['heavy_product_description']}\n"
            f"Image URL: {product['heavy_product_image_url']}\n"
            f"Created At: {product['heavy_product_created_at']}\n"
            f"Updated At: {product['heavy_product_updated_at']}\n"
            f"Employee Id: {product['employee_id']}\n"
            f"Employee Name: {product['employee_name']}\n"
            f"Employee Number: {product['employee_num']}\n"
            f"\n"
        )

    return body


def generate_updated_products_body(updated_fields, update_time, employee, product_id, product_name):
    """
    Generates a neatly formatted email body for product update notifications.

    :param updated_fields: Dictionary of updated fields and their new values.
    :param update_time: The time the product was updated.
    :param employee: The employee who made the updates.
    :param product_id: The ID of the product that was updated.
    :param product_name: The name of the product that was updated.
    :return: A formatted string representing the email body.
    """
    body = "Dear Inventory Team,\n\n"
    body += f"The following updates were made to the product name:- '{product_name}' and product id:- (ID: {product_id}) on {update_time}:\n\n"

    if employee:
        body += f"Updated by: {employee.emp_first_name} {employee.emp_last_name} (Employee Number: {employee.emp_num})\n\n"

    if not updated_fields:
        body += "No updates were made.\n"
    else:
        for field, value in updated_fields.items():
            body += f"- {field.replace('_', ' ').title()}: {value}\n"

    body += "\nPlease review the changes and ensure everything is correct.\n\n"
    body += "Best regards,\n"
    body += "Inventory Management System\n"

    return body


def generate_deleted_product_body(product_details, delete_time):
    """
    Generates a neatly formatted email body for product deletion notifications.

    :param product_details: Dictionary containing the details of the deleted product.
    :param delete_time: The time the product was deleted.
    :return: A formatted string representing the email body.
    """
    body = "Dear Inventory Team,\n\n"
    body += f"The following product was deleted on {delete_time}:\n\n"

    for key, value in product_details.items():
        body += f"- {key.replace('_', ' ').title()}: {value}\n"

    body += "\nPlease review the changes in the inventory.\n\n"
    body += "Best regards,\n"
    body += "Inventory Management System\n"

    return body


# --------------------------------------------  Dealer table -----------------------------------------------------------


def notify_success(subject, details):
    """
    Sends a success notification email with detailed information.

    :param subject: Subject of the success email.
    :param details: Detailed information to include in the email body.
    """
    body = f"Successful!\n\nDetails:\n********************************************\n{details}"
    send_email(RECEIVER_EMAIL, subject, body)


def notify_failure(subject, details):
    """
    Sends a failure notification email with detailed information.

    :param subject: Subject of the failure email.
    :param details: Detailed information to include in the email body.
    """
    body = f"Failure!\n\nDetails:\n********************************************\n{details}"
    send_email(ERROR_HANDLING_GROUP_EMAIL, subject, body)


# ----------------------------------------------  Opportunity table ----------------------------------------------------

def notify_opportunity_update_success(subject, details):
    """
    Sends a formatted success notification email for opportunity updates.

    :param subject: Subject of the email.
    :param details: Dictionary containing the details of the updated opportunity.
    """
    try:
        opportunity_id = details.get("opportunity_id", "N/A")
        updated_fields = details.get("updated_fields", {})

        if not updated_fields:
            log_warning(f"No fields were updated for Opportunity ID: {opportunity_id}")
            return

        email_content = (
            f"Dear Team,\n\n"
            f"The opportunity has been successfully updated with the following details:\n"
            f"********************************************\n"
            f"Opportunity ID: {opportunity_id}\n\nUpdated Fields:\n"
        )

        index = 1
        for field, label in [
            ("opportunity_name", "Opportunity Name"),
            ("account_name", "Account Name"),
            ("close_date", "Close Date"),
            ("amount", "Amount"),
            ("currency_conversions", "Currency Conversions"),
            ("description", "Description"),
            ("dealer_id", "Dealer ID"),
            ("dealer_code", "Dealer Code"),
            ("stage", "Stage"),
            ("probability", "Probability"),
            ("next_step", "Next Step"),
            ("amount_in_words", "Amount in Words"),
            ("vehicle_model", "Vehicle Model"),
            ("vehicle_year", "Vehicle Year")
        ]:
            if field in updated_fields:
                if field == "close_date":
                    formatted_date = updated_fields[field].strftime("%d %B %Y, %I:%M %p")
                    email_content += f"{index}. {label}: {formatted_date}\n"
                elif field == "currency_conversions":
                    email_content += f"{index}. {label}:\n"
                    for currency, value in updated_fields[field].items():
                        email_content += f"   - {currency.upper()}: {value:.2f}\n"
                elif field == "amount":
                    email_content += f"{index}. {label}: {updated_fields[field]:.2f}\n"
                else:
                    email_content += f"{index}. {label}: {updated_fields[field]}\n"
                index += 1

        email_content += "********************************************\n"
        email_content += "\nRegards,\nOpportunity Management Team"

        log_info(f"Opportunity update notification prepared for Opportunity ID: {opportunity_id}")

        send_email(RECEIVER_EMAIL, subject, email_content)
        log_info(f"Opportunity update email successfully sent for Opportunity ID: {opportunity_id}")

    except KeyError as e:
        session.rollback()
        log_error(f"KeyError encountered while processing the opportunity update: {str(e)}")
    except Exception as e:
        session.rollback()
        log_error(f"An unexpected error occurred while sending opportunity update email: {str(e)}")


def format_opportunities_for_email(opportunities):
    """
    Format opportunities data for email content with exception handling and logging.

    :param opportunities: List of opportunities in dictionary format.
    :return: Formatted email content as a string.
    """
    email_content = ""

    for opp in opportunities:
        try:
            email_content += (
                f"Opportunity ID: {opp.get('opportunity_id', 'N/A')}\n"
                f"Name: {opp.get('opportunity_name', 'N/A')}\n"
                f"Account: {opp.get('account_name', 'N/A')}\n"
                f"Amount: {opp.get('amount', 'N/A')}\n"
                f"Amount in Words: {opp.get('amount_in_words', 'N/A')}\n"
                f"Close Date: {opp.get('close_date', 'N/A')}\n"
                f"Created Date: {opp.get('created_date', 'N/A')}\n"
                f"Dealer ID: {opp.get('dealer_id', 'N/A')}\n"
                f"Dealer Code: {opp.get('dealer_code', 'N/A')}\n"
                f"Stage: {opp.get('stage', 'N/A')}\n"
                f"Probability: {opp.get('probability', 'N/A')}%\n"
                f"Next Step: {opp.get('next_step', 'N/A')}\n"
                f"Description: {opp.get('description', 'N/A')}\n"
                f"Currency Conversions:\n{opp.get('currency_conversions', 'N/A')}\n\n"
                f"Employee ID: {opp.get('employee_id', 'N/A')}\n"
                f"Employee Name: {opp.get('employee_name', 'N/A')}\n"
                f"Employee Number: {opp.get('employee_num', 'N/A')}\n"
                f"Product ID: {opp.get('product_id', 'N/A')}\n"
                f"Product Name: {opp.get('product_name', 'N/A')}\n"
                f"Product Brand: {opp.get('product_brand', 'N/A')}\n"
                f"Product Model: {opp.get('product_model', 'N/A')}\n"
                f"Product Image URL: {opp.get('product_image_url', 'N/A')}\n"
                f"********************************************\n\n"
            )
        except KeyError as e:
            session.rollback()
            log_error(
                f"KeyError while formatting opportunity: {str(e)} for opportunity ID {opp.get('opportunity_id', 'Unknown')}")
        except Exception as e:
            session.rollback()
            log_error(
                f"An unexpected error occurred while formatting opportunity ID {opp.get('opportunity_id', 'Unknown')}: {str(e)}")

    return email_content


def notify_opportunity_details(subject, opportunities, total_count):
    """
    Sends an email with detailed opportunity information including the total count, with exception handling and logging.

    :param subject: Subject of the email.
    :param opportunities: List of opportunities in dictionary format to include in the email body.
    :param total_count: Total number of opportunities.
    """
    try:
        log_info(f"Starting email notification for {total_count} opportunities with subject: {subject}")

        body = (
            f"Opportunity Details:\n"
            f"********************************************\n"
            f"Total Count of Opportunities: {total_count}\n\n"
        )

        for opp in opportunities:
            try:
                body += (
                    f"Opportunity ID: {opp.get('opportunity_id', 'N/A')}\n"
                    f"Name: {opp.get('opportunity_name', 'N/A')}\n"
                    f"Account: {opp.get('account_name', 'N/A')}\n"
                    f"Amount: {opp.get('amount', 'N/A')}\n"
                    f"Amount in Words: {opp.get('amount_in_words', 'N/A')}\n"
                    f"Close Date: {opp.get('close_date', 'N/A')}\n"
                    f"Created Date: {opp.get('created_date', 'N/A')}\n"
                    f"Dealer ID: {opp.get('dealer_id', 'N/A')}\n"
                    f"Dealer Code: {opp.get('dealer_code', 'N/A')}\n"
                    f"Stage: {opp.get('stage', 'N/A')}\n"
                    f"Probability: {opp.get('probability', 'N/A')}%\n"
                    f"Next Step: {opp.get('next_step', 'N/A')}\n"
                    f"Description: {opp.get('description', 'N/A')}\n"
                    f"Currency Conversions:\n{opp.get('currency_conversions', 'N/A')}\n\n"
                    f"Employee ID: {opp.get('employee_id', 'N/A')}\n"
                    f"Employee Name: {opp.get('employee_name', 'N/A')}\n"
                    f"Employee Number: {opp.get('employee_num', 'N/A')}\n"
                    f"Product ID: {opp.get('product_id', 'N/A')}\n"
                    f"Product Name: {opp.get('product_name', 'N/A')}\n"
                    f"Product Brand: {opp.get('product_brand', 'N/A')}\n"
                    f"Product Model: {opp.get('product_model', 'N/A')}\n"
                    f"Product Image URL: {opp.get('product_image_url', 'N/A')}\n"
                    f"********************************************\n\n"
                )
            except KeyError as e:
                session.rollback()
                log_error(
                    f"KeyError for opportunity ID {opp.get('opportunity_id', 'Unknown')}: Missing key {str(e)}")
            except Exception as e:
                session.rollback()
                log_error(
                    f"An unexpected error occurred while formatting opportunity ID {opp.get('opportunity_id', 'Unknown')}: {str(e)}")

        log_info("Email body prepared successfully, sending email...")

        send_email(RECEIVER_EMAIL, subject, body)

        log_info(f"Email sent successfully to {RECEIVER_EMAIL} with subject: {subject}")

    except Exception as e:
        log_error(f"An unexpected error occurred while generating or sending the email: {str(e)}")
        return "Error: Failed to send opportunity details email. Please check the logs for more information."


def send_opportunity_update_email(opportunity, updated_time):
    """
    Send an email with the updated opportunity details and return all the details.
    """
    try:
        employee_info = {
            "employee_name": f"{opportunity.employee.emp_first_name} {opportunity.employee.emplast_name}" if opportunity.employee else "N/A",
            "employee_id": opportunity.employee_id
        }

        product_info = {
            "product_id": opportunity.product_id,
            "product_name": opportunity.product_name,
            "product_brand": opportunity.product_brand,
            "product_model": opportunity.product_model,
            "product_image_url": opportunity.product_image_url
        }

        currency_conversions = opportunity.serialize_to_dict().get('currency_conversions',
                                                                   "No currency conversion details")

        email_subject = f"Opportunity Update Notification - {opportunity.opportunity_name}"
        email_body = f"""
        The following opportunity has been updated:

        Opportunity ID: {opportunity.opportunity_id}
        Opportunity Name: {opportunity.opportunity_name}
        Account Name: {opportunity.account_name}
        Close Date: {opportunity.close_date}
        Amount: {opportunity.amount} (In Words: {opportunity.amount_in_words})
        Description: {opportunity.description}
        Dealer Code: {opportunity.dealer_code}
        Stage: {opportunity.stage}
        Probability: {opportunity.probability}
        Next Step: {opportunity.next_step}

        Employee Details:
        Employee Name: {employee_info['employee_name']}
        Employee ID: {employee_info['employee_id']}

        Product Details:
        Product ID: {product_info['product_id']}
        Product Name: {product_info['product_name']}
        Product Brand: {product_info['product_brand']}
        Product Model: {product_info['product_model']}
        Product Image URL: {product_info['product_image_url']}

        Currency Conversions:
        {currency_conversions}

        Updated At: {updated_time}
        """

        log_debug(f"Preparing to send email with the following content: {email_body}")

        send_email(
            too_email=RECEIVER_EMAIL,
            subject=email_subject,
            body=email_body
        )

        opportunity_details = {
            "opportunity_id": opportunity.opportunity_id,
            "opportunity_name": opportunity.opportunity_name,
            "account_name": opportunity.account_name,
            "close_date": opportunity.close_date,
            "amount": opportunity.amount,
            "amount_in_words": opportunity.amount_in_words,
            "description": opportunity.description,
            "dealer_code": opportunity.dealer_code,
            "stage": opportunity.stage,
            "probability": opportunity.probability,
            "next_step": opportunity.next_step,
            "employee_details": employee_info,
            "product_details": product_info,
            "currency_conversions": currency_conversions,
            "updated_time": updated_time
        }

        log_info(f"Opportunity email sent successfully for Opportunity ID: {opportunity.opportunity_id}")

        return opportunity_details

    except Exception as e:
        session.rollback()
        log_error(f"Error while sending opportunity update email: {str(e)}")

        return {"error": f"Error while sending email: {str(e)}"}


def construct_success_message(deleted_customers_info):
    """
    Constructs a success message for deleted customers and sends it via email.

    :param deleted_customers_info: List of dictionaries containing deleted customer information.
    :return: Formatted success message string.
    """
    try:
        if not deleted_customers_info:
            return "No customers were deleted."

        message_lines = [
            "Customer(s) deleted successfully.\n",
            "Deleted Customers:\n"
        ]

        for info in deleted_customers_info:
            message_lines.append(
                f"Opportunity ID: {info['opportunity_id']}\n"
                f"Opportunity Name: {info['opportunity_name']}\n"
                f"Account Name: {info['account_name']}\n"
                f"Dealer ID: {info['dealer_id']}\n"
                f"Dealer Code: {info['dealer_code']}\n"
                f"Amount: {info['amount']}\n"
                f"Close Date: {info['close_date']}\n"
                f"Created Date: {info['created_date']}\n"
                f"Employee ID: {info['employee_id']}\n"
                f"Employee Name: {info['employee_name']}\n"
                f"Employee Number: {info['employee_num']}\n"
                f"Product ID: {info['product_id']}\n"
                f"Product Name: {info['product_name']}\n"
                f"Product Brand: {info['product_brand']}\n"
                f"Product Model: {info['product_model']}\n"
                "------------------------------------------\n"
            )

        final_message = "\n".join(message_lines)

        send_email(
            too_email=RECEIVER_EMAIL,
            subject="Deleted Customer Notification",
            body=final_message
        )

        return final_message

    except Exception as e:
        log_error(f"Error constructing success message: {str(e)}")
        return "An error occurred while constructing the success message."


# -------------------------------------------- Customers Table ---------------------------------------------------------


def generate_customer_email_body(customer):
    """
    Generates the email body for a newly added heavy machinery customer with logging and exception handling.

    :param customer: The HeavyMachineryCustomer object containing customer details.
    :return: A string formatted as the email body or a default error message in case of an exception.
    """
    try:
        log_info(f"Generating email body for customer: {customer.customer_name}")

        email_body = f"""
        Dear Management Team,

        We are pleased to report that a new customer has shown interest in our products.

        Here are the customer's details:
        - **Customer Name:** {customer.customer_name}
        - **Contact Information:** {customer.customer_contact_info}
        - **Address:** {customer.customer_address}
        - **Opportunity ID:** {customer.opportunity_id if customer.opportunity_id else 'N/A'}
        - **Status:** {customer.customer_status}
        - **Comments:** {customer.customer_comments if customer.customer_comments else 'No comments provided'}
        - **Feedback:** {customer.customer_feedback if customer.customer_feedback else 'No feedback provided'}
        - **Last Interaction:** {customer.customer_last_interaction.strftime('%Y-%m-%d') if customer.customer_last_interaction else 'No interaction yet'}
        - **Created At:** {customer.customer_created_at.strftime('%Y-%m-%d %H:%M:%S')}

        **Product Details**:
        - **Product Name:** {customer.product_name}
        - **Model:** {customer.product_model}
        - **Brand:** {customer.product_brand}

        Please review these details at your earliest convenience. If there are any additional actions required, let us know. We look forward to further engagement with this customer to build a successful partnership.

        Best Regards,
        Customer Relations Team
        """

        log_info(f"Email body successfully generated for customer: {customer.customer_name}")

        return email_body

    except AttributeError as e:
        log_error(f"AttributeError while generating email body: {str(e)}")
        return "Error: Missing required customer information. Please contact support."

    except Exception as e:
        log_error(f"An unexpected error occurred while generating email body: {str(e)}")
        return "Error: Unable to generate the email. Please contact support."


def generate_customers_email_body(customers, total_count):
    """
    Format customers data for email content with exception handling and logging.

    :param customers: List of customers in dictionary format.
    :param total_count: Total number of customers fetched.
    :return: Formatted email content as a string.
    """
    email_content = f"Total Customers Fetched: {total_count}\n\n"

    for customer in customers:
        try:
            email_content += (
                f"Customer ID: {customer.get('customer_id', 'N/A')}\n"
                f"Name: {customer.get('customer_name', 'N/A')}\n"
                f"Contact Info: {customer.get('customer_contact_info', 'N/A')}\n"
                f"Address: {customer.get('customer_address', 'N/A')}\n"
                f"Opportunity ID: {customer.get('opportunity_id', 'N/A')}\n"
                f"Dealer ID: {customer.get('dealer_id', 'N/A')}\n"
                f"Employee ID: {customer.get('employee_id', 'N/A')}\n"
                f"Status: {customer.get('customer_status', 'N/A')}\n"
                f"Comments: {customer.get('customer_comments', 'N/A')}\n"
                f"Feedback: {customer.get('customer_feedback', 'N/A')}\n"
                f"Last Interaction: {customer.get('customer_last_interaction', 'N/A')}\n"
                f"Product ID: {customer.get('product_id', 'N/A')}\n"
                f"Product Name: {customer.get('product_name', 'N/A')}\n"
                f"Product Brand: {customer.get('product_brand', 'N/A')}\n"
                f"Product Model: {customer.get('product_model', 'N/A')}\n"
                "********************************************\n\n"
            )
        except KeyError as e:
            log_error(
                f"KeyError while formatting customer: {str(e)} for customer ID {customer.get('customer_id', 'Unknown')}")
        except Exception as e:
            log_error(
                f"An unexpected error occurred while formatting customer ID {customer.get('customer_id', 'Unknown')}: {str(e)}")

    return email_content


def format_update_customers_email_content(customers, updated_time, employee):
    """
    Format customers data for email content with exception handling and logging.

    :param customers: List of customers in dictionary format.
    :param updated_time: The time when the customer details were last updated.
    :param employee: The employee who made the updates.
    :return: Formatted email content as a string.
    """
    email_content = f"Dear Inventory Team,\n\n"
    email_content += f"The following customer updates were made on {updated_time}:\n\n"

    if employee:
        email_content += f"Updated by: {employee.emp_first_name} {employee.emp_last_name} (Employee Number: {employee.emp_num})\n\n"

    if not customers:
        email_content += "No customers were updated.\n"
    else:
        for customer in customers:
            try:
                email_content += (
                    f"Customer ID: {customer.get('customer_id', 'N/A')}\n"
                    f"Name: {customer.get('customer_name', 'N/A')}\n"
                    f"Contact Info: {customer.get('customer_contact_info', 'N/A')}\n"
                    f"Address: {customer.get('customer_address', 'N/A')}\n"
                    f"Opportunity ID: {customer.get('opportunity_id', 'N/A')}\n"
                    f"Dealer ID: {customer.get('dealer_id', 'N/A')}\n"
                    f"Employee ID: {customer.get('employee_id', 'N/A')}\n"
                    f"Status: {customer.get('customer_status', 'N/A')}\n"
                    f"Comments: {customer.get('customer_comments', 'N/A')}\n"
                    f"Feedback: {customer.get('customer_feedback', 'N/A')}\n"
                    f"Last Interaction: {customer.get('customer_last_interaction', 'N/A')}\n"
                    f"Product ID: {customer.get('product_id', 'N/A')}\n"
                    f"Product Name: {customer.get('product_name', 'N/A')}\n"
                    f"Product Brand: {customer.get('product_brand', 'N/A')}\n"
                    f"Product Model: {customer.get('product_model', 'N/A')}\n"
                    "********************************************\n\n"
                )
            except KeyError as e:
                log_error(
                    f"KeyError while formatting customer: {str(e)} for customer ID {customer.get('customer_id', 'Unknown')}")
            except Exception as e:
                log_error(
                    f"An unexpected error occurred while formatting customer ID {customer.get('customer_id', 'Unknown')}: {str(e)}")

    email_content += "Please review the changes and ensure everything is correct.\n\n"
    email_content += "Best regards,\n"
    email_content += "Customer Management System\n"

    return email_content


def send_customer_deletion_email(customer_details, deletion_time):
    """
    Send an email notification about the deletion of a customer.

    :param customer_details: Dictionary containing customer information.
    :param deletion_time: The timestamp when the customer was deleted.
    """
    email_body = (
        f"Dear Inventory Team,\n\n"
        f"The following customer has been deleted on {deletion_time}:\n\n"
        f"Customer ID: {customer_details.get('customer_id')}\n"
        f"Name: {customer_details.get('customer_name')}\n"
        f"Contact Info: {customer_details.get('customer_contact_info')}\n"
        f"Address: {customer_details.get('customer_address')}\n\n"
        "Please review the records for confirmation.\n\n"
        "Best regards,\n"
        "Customer Management System"
    )

    try:
        send_email(RECEIVER_EMAIL, f"Customer {customer_details.get('customer_id')} Deleted", email_body)
        log_info(f"Email notification sent for customer ID {customer_details.get('customer_id')} deletion.")
    except Exception as e:
        log_error(f"Failed to send email notification for customer deletion: {str(e)}")
