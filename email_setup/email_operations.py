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
    Dear {employee.first_name} {employee.last_name},

    Welcome to the team! We are excited to have you join us as a {employee.position} in the {employee.department} department.

    Here are your details:
    - **Employee Id:** {employee.id}
    - **Full Name:** {employee.first_name} {employee.last_name}
    - **Email:** {employee.emp_email}
    - **Employee Number:** {employee.emp_num}
    - **Phone:** {employee.phone}
    - **Hire Date:** {employee.hire_date.strftime('%Y-%m-%d')}
    - **Position:** {employee.position}
    - **Salary:** ${employee.salary:,.2f}
    - **Age:** {employee.age}
    - **Sex:** {employee.sex}
    - **Blood Group:** {employee.blood_group}
    - **Height:** {employee.height} cm
    - **Weight:** {employee.weight} kg
    - **Address:** {employee.address}
    - **Emergency Contact:** {employee.emergency_contact}
    - **Nationality:** {employee.nationality}
    - **Date of Birth:** {employee.date_of_birth.strftime('%Y-%m-%d')}
    - **Marital Status:** {employee.marital_status}
    - **Employment Status:** {employee.employment_status}
    - **Insurance Number:** {employee.insurance_number}
    - **Created At:** {employee.created_at}

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
            f"Employee Id: {emp['id']}\n"
            f"Name: {emp['first_name']} {emp['last_name']}\n"
            f"Employee Number: {emp['emp_num']}\n"
            f"Email: {emp['emp_email']}\n"
            f"Phone: {emp['phone']}\n"
            f"Position: {emp['position']}\n"
            f"Department: {emp['department']}\n"
            f"Salary: {emp['salary']}\n"
            f"Age: {emp['age']}\n"
            f"Sex: {emp['sex']}\n"
            f"Blood Group: {emp['blood_group']}\n"
            f"Height: {emp['height']}\n"
            f"Weight: {emp['weight']}\n"
            f"Address: {emp['address']}\n"
            f"Emergency Contact: {emp['emergency_contact']}\n"
            f"Nationality: {emp['nationality']}\n"
            f"Date of Birth: {emp['date_of_birth']}\n"
            f"Marital Status: {emp['marital_status']}\n"
            f"Employment Status: {emp['employment_status']}\n"
            f"Insurance Number: {emp['insurance_number']}\n"
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

    The details of employee ID {updated_employee['id']} were successfully updated on {update_time}.

    Updated Details:
    First Name: {updated_employee.get('first_name', 'N/A')}
    Last Name: {updated_employee.get('last_name', 'N/A')}
    Email: {updated_employee.get('emp_email', 'N/A')}
    Employee Number: {updated_employee.get('emp_num', 'N/A')}
    Phone: {updated_employee.get('phone', 'N/A')}
    Position: {updated_employee.get('position', 'N/A')}
    Salary: {updated_employee.get('salary', 'N/A')}
    Department: {updated_employee.get('department', 'N/A')}
    Hire Date: {updated_employee.get('hire_date', 'N/A')}
    Age: {updated_employee.get('age', 'N/A')}
    Sex: {updated_employee.get('sex', 'N/A')}
    Blood Group: {updated_employee.get('blood_group', 'N/A')}
    Height: {updated_employee.get('height', 'N/A')}
    Weight: {updated_employee.get('weight', 'N/A')}
    Address: {updated_employee.get('address', 'N/A')}
    Emergency Contact: {updated_employee.get('emergency_contact', 'N/A')}
    Nationality: {updated_employee.get('nationality', 'N/A')}
    Date of Birth: {updated_employee.get('date_of_birth', 'N/A')}
    Marital Status: {updated_employee.get('marital_status', 'N/A')}
    Employment Status: {updated_employee.get('employment_status', 'N/A')}
    Insurance Number: {updated_employee.get('insurance_number', 'N/A')}

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
    body = f"Employee {employee.first_name} {employee.last_name} (ID: {employee.id}) has been deleted from the system.\n\n"
    body += "Deleted Employee Details:\n"
    body += f"Employee Number: {employee.emp_num}\n"
    body += f"Email: {employee.emp_email}\n"
    body += f"Phone: {employee.phone}\n"
    body += f"Position: {employee.position}\n"
    body += f"Department: {employee.department}\n"
    body += f"Hire Date: {employee.hire_date}\n"
    body += f"Age: {employee.age}\n"
    body += f"Sex: {employee.sex}\n"
    body += f"Blood Group: {employee.blood_group}\n"
    body += f"Height: {employee.height}\n"
    body += f"Weight: {employee.weight}\n"
    body += f"Address: {employee.address}\n"
    body += f"Emergency Contact: {employee.emergency_contact}\n"
    body += f"Nationality: {employee.nationality}\n"
    body += f"Date of Birth: {employee.date_of_birth}\n"
    body += f"Marital Status: {employee.marital_status}\n"
    body += f"Employment Status: {employee.employment_status}\n"
    body += f"Insurance Number: {employee.insurance_number}\n"
    body += f"Created At: {employee.created_at}\n"
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
    - **Product ID:** {product.id}
    - **Name:** {product.name}
    - **Type:** {product.type}
    - **Brand:** {product.brand}
    - **Model:** {product.model}
    - **Year of Manufacture:** {product.year_of_manufacture}
    - **Price:** ${product.price:,.2f}
    - **Weight:** {product.weight} kg
    - **Dimensions:** {product.dimensions}
    - **Engine Type:** {product.engine_type}
    - **Horsepower:** {product.horsepower}
    - **Fuel Capacity:** {product.fuel_capacity} liters
    - **Operational Hours:** {product.operational_hours}
    - **Warranty Period:** {product.warranty_period} months
    - **Status:** {product.status}
    - **Description:** {product.description}
    - **Image URL:** {product.image_url}
    - **Created At:** {product.created_at.isoformat()}
    - **Updated At:** {product.updated_at.isoformat()}

    **Employee Details:**
    - **Employee ID:** {employee.id}
    - **Name:** {employee.first_name} {employee.last_name}
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
            f"Product Id: {product['id']}\n"
            f"Name: {product['name']}\n"
            f"Product Type: {product['type']}\n"
            f"Brand: {product['brand']}\n"
            f"Model: {product['model']}\n"
            f"Year of Manufacture: {product['year_of_manufacture']}\n"
            f"Price: {product['price']}\n"
            f"Weight: {product['weight']} kg\n"
            f"Dimensions: {product['dimensions']}\n"
            f"Engine Type: {product['engine_type']}\n"
            f"Horsepower: {product['horsepower']} hp\n"
            f"Fuel Capacity: {product['fuel_capacity']} liters\n"
            f"Operational Hours: {product['operational_hours']}\n"
            f"Warranty Period: {product['warranty_period']} months\n"
            f"Status: {product['status']}\n"
            f"Description: {product['description']}\n"
            f"Image URL: {product['image_url']}\n"
            f"Created At: {product['created_at']}\n"
            f"Updated At: {product['updated_at']}\n"
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
        body += f"Updated by: {employee.first_name} {employee.last_name} (Employee Number: {employee.emp_num})\n\n"

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
    opportunity_id = details.get("opportunity_id")
    updated_fields = details.get("updated_fields", {})

    # Build the email content (email body)
    email_content = f"Dear Team,\n\nThe opportunity has been successfully updated with the following details:\n"
    email_content += "********************************************\n"
    email_content += f"Opportunity ID: {opportunity_id}\n\nUpdated Fields:\n"

    # Formatting updated fields
    index = 1
    if "opportunity_name" in updated_fields:
        email_content += f"{index}. Opportunity Name: {updated_fields['opportunity_name']}\n"
        index += 1
    if "account_name" in updated_fields:
        email_content += f"{index}. Account Name: {updated_fields['account_name']}\n"
        index += 1
    if "close_date" in updated_fields:
        close_date = updated_fields['close_date'].strftime("%d %B %Y, %I:%M %p")
        email_content += f"{index}. Close Date: {close_date}\n"
        index += 1
    if "amount" in updated_fields:
        email_content += f"{index}. Amount: {updated_fields['amount']:.2f}\n"
        index += 1
    if "currency_conversions" in updated_fields:
        conversions = updated_fields['currency_conversions']
        email_content += f"{index}. Currency Conversions:\n"
        for currency, value in conversions.items():
            email_content += f"   - {currency.upper()}: {value:.2f}\n"
        index += 1
    if "description" in updated_fields:
        email_content += f"{index}. Description: {updated_fields['description']}\n"
        index += 1
    if "dealer_id" in updated_fields:
        email_content += f"{index}. Dealer ID: {updated_fields['dealer_id']}\n"
        index += 1
    if "dealer_code" in updated_fields:
        email_content += f"{index}. Dealer Code: {updated_fields['dealer_code']}\n"
        index += 1
    if "stage" in updated_fields:
        email_content += f"{index}. Stage: {updated_fields['stage']}\n"
        index += 1
    if "probability" in updated_fields:
        email_content += f"{index}. Probability: {updated_fields['probability']}%\n"
        index += 1
    if "next_step" in updated_fields:
        email_content += f"{index}. Next Step: {updated_fields['next_step']}\n"
        index += 1
    if "amount_in_words" in updated_fields:
        email_content += f"{index}. Amount in Words: {updated_fields['amount_in_words']}\n"
        index += 1
    if "vehicle_model" in updated_fields:
        email_content += f"{index}. Vehicle Model: {updated_fields['vehicle_model']}\n"
        index += 1
    if "vehicle_year" in updated_fields:
        email_content += f"{index}. Vehicle Year: {updated_fields['vehicle_year']}\n"
        index += 1

    email_content += "********************************************\n"
    email_content += "\nRegards,\nOpportunity Management Team"

    # Send the email with the correct recipient list
    send_email(RECEIVER_EMAIL, subject, email_content)


def format_opportunities_for_email(opportunities):
    """
    Format opportunities data for email content.

    :param opportunities: List of opportunities in dictionary format
    :return: str
    """
    email_content = ""
    for opp in opportunities:
        email_content += (
            f"Opportunity ID: {opp['opportunity_id']}\n"
            f"Name: {opp['opportunity_name']}\n"
            f"Account: {opp['account_name']}\n"
            f"Amount: {opp['amount']}\n"
            f"Amount in Words: {opp['amount_in_words']}\n"
            f"Close Date: {opp['close_date']}\n"
            f"Created Date: {opp['created_date']}\n"
            f"Dealer ID: {opp['dealer_id']}\n"
            f"Dealer Code: {opp['dealer_code']}\n"
            f"Stage: {opp['stage']}\n"
            f"Probability: {opp['probability']}%\n"
            f"Next Step: {opp['next_step']}\n"
            f"Description: {opp['description']}\n"
            f"Currency Conversions:\n{opp['currency_conversions']}\n\n"
            f"Employee ID: {opp['employee_id']}\n"
            f"Employee Name: {opp['employee_name']}\n"
            f"Employee Number: {opp['employee_num']}\n"
            f"Product ID: {opp['product_id']}\n"
            f"Product Name: {opp['product_name']}\n"
            f"Product Brand: {opp['product_brand']}\n"
            f"Product Model: {opp['product_model']}\n"
            f"Product Image URL: {opp['product_image_url']}\n"
            f"********************************************\n\n"
        )
    return email_content


def notify_opportunity_details(subject, opportunities, total_count):
    """
    Sends an email with detailed opportunity information including the total count.

    :param subject: Subject of the email.
    :param opportunities: List of opportunities in dictionary format to include in the email body.
    :param total_count: Total number of opportunities.
    """
    body = (
        f"Opportunity Details:\n"
        f"********************************************\n"
        f"Total Count of Opportunities: {total_count}\n\n"
    )

    # Format opportunities data for the email content
    for opp in opportunities:
        body += (
            f"Opportunity ID: {opp['opportunity_id']}\n"
            f"Name: {opp['opportunity_name']}\n"
            f"Account: {opp['account_name']}\n"
            f"Amount: {opp['amount']}\n"
            f"Amount in Words: {opp['amount_in_words']}\n"
            f"Close Date: {opp['close_date']}\n"
            f"Created Date: {opp['created_date']}\n"
            f"Dealer ID: {opp['dealer_id']}\n"
            f"Dealer Code: {opp['dealer_code']}\n"
            f"Stage: {opp['stage']}\n"
            f"Probability: {opp['probability']}%\n"
            f"Next Step: {opp['next_step']}\n"
            f"Description: {opp['description']}\n"
            f"Currency Conversions:\n{opp['currency_conversions']}\n\n"
            f"Employee ID: {opp['employee_id']}\n"
            f"Employee Name: {opp['employee_name']}\n"
            f"Employee Number: {opp['employee_num']}\n"
            f"Product ID: {opp['product_id']}\n"
            f"Product Name: {opp['product_name']}\n"
            f"Product Brand: {opp['product_brand']}\n"
            f"Product Model: {opp['product_model']}\n"
            f"Product Image URL: {opp['product_image_url']}\n"
            f"********************************************\n\n"
        )

    send_email(RECEIVER_EMAIL, subject, body)
