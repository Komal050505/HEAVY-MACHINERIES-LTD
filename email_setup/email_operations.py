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
    SMTP_PORT
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


# -------------------------------------------- Heavy Machineries table ----------------------------------------------------------
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
