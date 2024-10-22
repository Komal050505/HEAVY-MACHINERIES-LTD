from datetime import datetime

from flask import Flask, jsonify, request
from sqlalchemy.exc import IntegrityError

from App.constants import REQUIRED_FIELDS_FOR_EMPLOYEE_TABLE
from Db_connections.configurations import session
from Logging_package.logging_utility import log_info, log_warning, log_error, log_debug
from User_models.tables import Employee
from email_setup.email_config import RECEIVER_EMAIL
from email_setup.email_operations import generate_employee_email_body, send_email, generate_employee_notification_body, \
    generate_update_notification_body, generate_delete_notification
from Utilities.reusables import otp_required, validate_email

app = Flask(__name__)


@app.route('/add-employee', methods=['POST'])
@otp_required
def add_employee():
    """
    Add a new employee to the database.

    This endpoint receives a JSON object containing employee details, validates the input,
    and adds a new employee record if all validations pass.

    The required fields are:
    - first_name
    - last_name
    - emp_email
    - emp_num
    - phone
    - hire_date
    - position
    - salary
    - department
    - age
    - sex
    - blood_group
    - height
    - weight
    - address
    - emergency_contact
    - nationality
    - date_of_birth
    - marital_status
    - employment_status
    - insurance_number

    Validations include checking for required fields, ensuring valid email format,
    positive salary and age, and correct date formats.

    Upon successful addition, a welcome email is sent to the new employee.
    :return:JSON response with a success message and employee details if successful.
    """
    log_info(f"Entered /add-employee endpoint. Request method: {request.method}")

    try:
        data = request.get_json()
        log_debug(f"Received request data: {data}")

        for field in REQUIRED_FIELDS_FOR_EMPLOYEE_TABLE:
            if field not in data:
                log_warning(f"Missing field: {field} in request data")
                return jsonify({"message": f"Missing field: {field}"}), 400

        if not validate_email(data['emp_email']):
            log_warning(f"Invalid email format: {data['emp_email']}")
            return jsonify({"message": "Invalid email format"}), 400

        if not data.get('emp_num'):
            log_warning("Missing emp_num in request data")
            return jsonify({"message": "emp_num is required"}), 400

        if 'salary' in data and (data['salary'] <= 0):
            log_warning(f"Invalid salary: {data['salary']} - must be positive")
            return jsonify({"message": "Salary must be a positive number"}), 400

        if 'age' in data and (data['age'] <= 0):
            log_warning(f"Invalid age: {data['age']} - must be positive")
            return jsonify({"message": "Age must be a positive number"}), 400

        if 'sex' in data and data['sex'] not in ['Male', 'Female', 'Other']:
            log_warning(f"Invalid sex: {data['sex']}")
            return jsonify({"message": "Sex must be 'Male', 'Female', or 'Other'"}), 400

        try:
            hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d')
        except ValueError:
            log_warning(f"Invalid hire date format: {data['hire_date']}")
            return jsonify({"message": "Hire date must be in YYYY-MM-DD format"}), 400

        try:
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
        except ValueError:
            log_warning(f"Invalid date of birth format: {data['date_of_birth']}")
            return jsonify({"message": "Date of birth must be in YYYY-MM-DD format"}), 400

        # Create new employee record
        new_employee = Employee(
            first_name=data['first_name'],
            last_name=data['last_name'],
            emp_email=data['emp_email'],
            emp_num=data['emp_num'],
            phone=data.get('phone'),
            hire_date=hire_date,
            position=data['position'],
            salary=data['salary'],
            department=data['department'],
            age=data['age'],
            sex=data['sex'],
            blood_group=data.get('blood_group'),
            height=data.get('height'),
            weight=data.get('weight'),
            address=data.get('address'),
            emergency_contact=data.get('emergency_contact'),
            nationality=data.get('nationality'),
            date_of_birth=date_of_birth,
            marital_status=data['marital_status'],
            employment_status=data['employment_status'],
            insurance_number=data['insurance_number']
        )

        log_info(f"New employee created: {new_employee.emp_email} - Ready for database insertion")

        session.add(new_employee)
        session.commit()
        log_info(f"Employee {new_employee.emp_email} added successfully to the database")

        email_body = generate_employee_email_body(new_employee)
        send_email(RECEIVER_EMAIL, "Welcome to the Team", email_body)
        log_info(f"Welcome email sent to {new_employee.emp_email}")

        return jsonify({"message": "Employee added successfully!", "employee": new_employee.to_dict()}), 201

    except IntegrityError as e:
        session.rollback()
        log_error(f"Database Integrity Error: {str(e)}")
        return jsonify({"message": "An employee with this email already exists."}), 409
    except Exception as e:
        session.rollback()
        log_error(f"General Error adding employee: {str(e)}")
        return jsonify({"message": f"Error adding employee: {str(e)}"}), 500
    finally:
        session.close()
        log_info("Session closed for add employee API")


@app.route('/get-employees', methods=['GET'])
def get_employees():
    """
    Fetch employee details from the database based on query parameters.
    If no parameters are provided, all employee records are returned.

    Query parameters:
    first_name (optional)
    last_name (optional)
    emp_email (optional)
    emp_num (optional)
    phone (optional)
    position (optional)
    department (optional)
    hire_date (optional)
    age (optional)
    sex (optional)
    blood_group (optional)
    height (optional)
    weight (optional)
    address (optional)
    emergency_contact (optional)
    nationality (optional)
    date_of_birth (optional)
    marital_status (optional)
    employment_status (optional)
    insurance_number (optional)
    created_at (optional)

    Returns:
     JSON response with employee details and total count.
    """
    log_info("Entered /get-employees endpoint.")
    try:
        emp_id = request.args.get('id')
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        emp_email = request.args.get('emp_email')
        emp_num = request.args.get('emp_num')
        phone = request.args.get('phone')
        position = request.args.get('position')
        salary = request.args.get('salary')
        department = request.args.get('department')
        hire_date = request.args.get('hire_date')
        age = request.args.get('age')
        sex = request.args.get('sex')
        blood_group = request.args.get('blood_group')
        height = request.args.get('height')
        weight = request.args.get('weight')
        address = request.args.get('address')
        emergency_contact = request.args.get('emergency_contact')
        nationality = request.args.get('nationality')
        date_of_birth = request.args.get('date_of_birth')
        marital_status = request.args.get('marital_status')
        employment_status = request.args.get('employment_status')
        insurance_number = request.args.get('insurance_number')
        created_at = request.args.get('created_at')

        log_info(f"Query parameters: {request.args}")

        query = session.query(Employee)

        if emp_id:
            log_debug(f"Filtering by emp_id: {emp_id}")
            query = query.filter(Employee.id == emp_id)
        if first_name:
            log_debug(f"Filtering by first_name: {first_name}")
            query = query.filter(Employee.first_name.ilike(f'%{first_name}%'))
        if last_name:
            log_debug(f"Filtering by last_name: {last_name}")
            query = query.filter(Employee.last_name.ilike(f'%{last_name}%'))
        if emp_email:
            log_debug(f"Filtering by emp_email: {emp_email}")
            query = query.filter(Employee.emp_email.ilike(f'%{emp_email}%'))
        if emp_num:
            log_debug(f"Filtering by emp_num: {emp_num}")
            query = query.filter(Employee.emp_num == emp_num)
        if phone:
            log_debug(f"Filtering by phone: {phone}")
            query = query.filter(Employee.phone.ilike(f'%{phone}%'))
        if position:
            log_debug(f"Filtering by position: {position}")
            query = query.filter(Employee.position.ilike(f'%{position}%'))
        if salary:
            log_debug(f"Filtering by salary: {salary}")
            query = query.filter(Employee.salary == salary)
        if department:
            log_debug(f"Filtering by department: {department}")
            query = query.filter(Employee.department.ilike(f'%{department}%'))
        if hire_date:
            log_debug(f"Filtering by hire_date: {hire_date}")
            query = query.filter(Employee.hire_date == hire_date)
        if age:
            log_debug(f"Filtering by age: {age}")
            query = query.filter(Employee.age == age)
        if sex:
            log_debug(f"Filtering by sex: {sex}")
            query = query.filter(Employee.sex.ilike(f'%{sex}%'))
        if blood_group:
            log_debug(f"Filtering by blood_group: {blood_group}")
            query = query.filter(Employee.blood_group.ilike(f'%{blood_group}%'))
        if height:
            log_debug(f"Filtering by height: {height}")
            query = query.filter(Employee.height == height)
        if weight:
            log_debug(f"Filtering by weight: {weight}")
            query = query.filter(Employee.weight == weight)
        if address:
            log_debug(f"Filtering by address: {address}")
            query = query.filter(Employee.address.ilike(f'%{address}%'))
        if emergency_contact:
            log_debug(f"Filtering by emergency_contact: {emergency_contact}")
            query = query.filter(Employee.emergency_contact.ilike(f'%{emergency_contact}%'))
        if nationality:
            log_debug(f"Filtering by nationality: {nationality}")
            query = query.filter(Employee.nationality.ilike(f'%{nationality}%'))
        if date_of_birth:
            log_debug(f"Filtering by date_of_birth: {date_of_birth}")
            query = query.filter(Employee.date_of_birth == date_of_birth)
        if marital_status:
            log_debug(f"Filtering by marital_status: {marital_status}")
            query = query.filter(Employee.marital_status.ilike(f'%{marital_status}%'))
        if employment_status:
            log_debug(f"Filtering by employment_status: {employment_status}")
            query = query.filter(Employee.employment_status.ilike(f'%{employment_status}%'))
        if insurance_number:
            log_debug(f"Filtering by insurance_number: {insurance_number}")
            query = query.filter(Employee.insurance_number.ilike(f'%{insurance_number}%'))
        if created_at:
            log_debug(f"Filtering by created_at: {created_at}")
            query = query.filter(Employee.created_at == created_at)

        employees = query.all()
        total_count = query.count()

        employee_list = [employee.to_dict() for employee in employees]
        log_info(f"Fetched {len(employee_list)} employee(s).")

        email_body = generate_employee_notification_body(employee_list, total_count)
        send_email(RECEIVER_EMAIL, "Employee Details Fetched", email_body)

        return jsonify({"total_count": total_count, "employees": employee_list}), 200

    except Exception as e:
        session.rollback()
        log_error(f"Error fetching employees: {str(e)}")
        return jsonify({"message": f"Error fetching employees: {str(e)}"}), 500
    finally:
        session.close()
        log_info("Closed /get-employees endpoint.")


@app.route('/update-employee', methods=['PUT'])
@otp_required
def update_employee():
    """
     Update an employee's details. All fields except 'id' can be edited.

    Request Body Parameters:
    id (required)
    first_name (optional)
    last_name (optional)
    emp_email (optional)
    emp_num (optional)
    phone (optional)
    position (optional)
    salary (optional)
    department (optional)
    hire_date (optional)
    age (optional)
    sex (optional)
    blood_group (optional)
    height (optional)
    weight (optional)
    address (optional)
    emergency_contact (optional)
    nationality (optional)
    date_of_birth (optional)
    marital_status (optional)
    employment_status (optional)
    insurance_number (optional)

    :return: JSON response with the updated employee details.
    """
    log_info("Entered /update-employee endpoint.")

    emp_id = None
    try:
        data = request.json
        log_debug(f"Request body received: {data}")

        emp_id = data.get('id')
        if not emp_id:
            log_warning("Employee ID not provided in the request.")
            return jsonify({"message": "Employee ID is required."}), 400

        log_info(f"Fetching employee with ID: {emp_id}")
        employee = session.query(Employee).filter_by(id=emp_id).first()

        if not employee:
            log_warning(f"Employee with ID {emp_id} not found.")
            return jsonify({"message": "Employee not found."}), 404

        log_info(f"Current employee details: {employee.to_dict()}")

        employee.first_name = data.get('first_name', employee.first_name)
        employee.last_name = data.get('last_name', employee.last_name)
        employee.emp_email = data.get('emp_email', employee.emp_email)
        employee.emp_num = data.get('emp_num', employee.emp_num)
        employee.phone = data.get('phone', employee.phone)
        employee.position = data.get('position', employee.position)
        employee.salary = data.get('salary', employee.salary)
        employee.department = data.get('department', employee.department)
        employee.hire_date = data.get('hire_date', employee.hire_date)
        employee.age = data.get('age', employee.age)
        employee.sex = data.get('sex', employee.sex)
        employee.blood_group = data.get('blood_group', employee.blood_group)
        employee.height = data.get('height', employee.height)
        employee.weight = data.get('weight', employee.weight)
        employee.address = data.get('address', employee.address)
        employee.emergency_contact = data.get('emergency_contact', employee.emergency_contact)
        employee.nationality = data.get('nationality', employee.nationality)
        employee.date_of_birth = data.get('date_of_birth', employee.date_of_birth)
        employee.marital_status = data.get('marital_status', employee.marital_status)
        employee.employment_status = data.get('employment_status', employee.employment_status)
        employee.insurance_number = data.get('insurance_number', employee.insurance_number)

        log_info(f"Updated employee details (before commit): {employee.to_dict()}")

        session.commit()
        log_info(f"Employee with ID {emp_id} updated successfully in the database.")

        updated_employee = employee.to_dict()
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_info(f"Employee ID {emp_id} updated at {update_time}.")

        email_body = generate_update_notification_body(updated_employee, update_time)
        send_email(RECEIVER_EMAIL, f"Employee {emp_id} Updated", email_body)
        log_info(f"Email notification sent for employee ID {emp_id} update.")

        return jsonify({
            "message": "Employee updated successfully.",
            "updated_employee": updated_employee
        }), 200

    except Exception as e:
        session.rollback()
        log_error(f"Error updating employee ID {emp_id}: {str(e)}")
        return jsonify({"message": f"Error updating employee: {str(e)}"}), 500

    finally:
        session.close()
        log_info("Closed /update-employee API session.")


@app.route('/delete-employee', methods=['DELETE'])
@otp_required
def delete_employee():
    """
    Delete an employee from the database based on provided identifiers.

    Query parameters:
    - id (optional)
    - emp_num (optional)
    - emp_email (optional)
    - phone (optional)

    Returns:
    - JSON response with complete details of the deleted employee and a success message.
    """
    log_info("Entered /delete-employee endpoint.")

    try:
        employee_id = request.args.get('id')
        emp_num = request.args.get('emp_num')
        emp_email = request.args.get('emp_email')
        phone = request.args.get('phone')

        log_debug(
            f"Query parameters received: id={employee_id}, emp_num={emp_num}, emp_email={emp_email}, phone={phone}")

        query = session.query(Employee)

        if employee_id:
            log_info(f"Filtering employee by ID: {employee_id}")
            query = query.filter(Employee.id == employee_id)
        elif emp_num:
            log_info(f"Filtering employee by emp_num: {emp_num}")
            query = query.filter(Employee.emp_num == emp_num)
        elif emp_email:
            log_info(f"Filtering employee by email: {emp_email}")
            query = query.filter(Employee.emp_email == emp_email)
        elif phone:
            log_info(f"Filtering employee by phone: {phone}")
            query = query.filter(Employee.phone == phone)
        else:
            log_warning("No identifier provided in request")
            return jsonify({"message": "Please provide at least one identifier (id, emp_num, emp_email, phone)."}), 400

        employee = query.first()
        if not employee:
            log_warning(f"No employee found for provided identifiers")
            return jsonify({"message": "Employee not found."}), 404

        log_info(f"Employee found for deletion: {employee.to_dict()}")

        employee_details = {
            "id": employee.id,
            "emp_num": employee.emp_num,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "emp_email": employee.emp_email,
            "phone": employee.phone,
            "position": employee.position,
            "department": employee.department,
            "hire_date": str(employee.hire_date),
            "age": employee.age,
            "sex": employee.sex,
            "blood_group": employee.blood_group,
            "height": employee.height,
            "weight": employee.weight,
            "address": employee.address,
            "emergency_contact": employee.emergency_contact,
            "nationality": employee.nationality,
            "date_of_birth": str(employee.date_of_birth),
            "marital_status": employee.marital_status,
            "employment_status": employee.employment_status,
            "insurance_number": employee.insurance_number,
            "created_at": str(employee.created_at)
        }

        deleted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_info(f"Deleting employee with ID {employee.id}")
        session.delete(employee)
        session.commit()
        log_info(f"Successfully deleted employee with ID {employee.id}")

        email_body = generate_delete_notification(employee, deleted_time)
        send_email(RECEIVER_EMAIL, "Employee Deleted", email_body)
        log_info(f"Email notification sent for deleted employee ID: {employee.id}")

        return jsonify({
                "message": f"Employee with ID {employee.id} has been deleted successfully.",
                "deleted_employee_details": employee_details,
                "deleted_time": deleted_time
            }), 20

    except Exception as e:
        session.rollback()
        log_error(f"Error deleting employee: {str(e)}")
        return jsonify({"message": f"Error deleting employee: {str(e)}"}), 500

    finally:
        session.close()
        log_info("Closed delete employee API")


if __name__ == "__main__":
    log_info(f"Starting the Flask application {app}.")
    app.run(debug=True)
    log_info("Flask application has stopped.")
