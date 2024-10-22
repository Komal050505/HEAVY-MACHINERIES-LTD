from sqlalchemy import Column, String, Integer, Numeric, DateTime, func, UUID, Text, CheckConstraint, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# -------------------------------------------- OTP STORE TABLE ---------------------------------------------------------
class OTPStore(Base):
    __tablename__ = 'otp_store'

    """
    Represents a one-time password (OTP) storage in the system.

    Attributes:
        id (int): Unique identifier for the OTP entry.
        email (str): The email address associated with the OTP.
        otp (str): The one-time password generated for the user.
        timestamp (datetime): The time when the OTP was generated.

    Methods:
        to_dict(): Converts the OTPStore object to a dictionary for JSON response.
    """

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    otp = Column(String(6), nullable=False)
    timestamp = Column(DateTime, nullable=False)

    def __init__(self, email, otp, timestamp):
        """Initialize an OTPStore object with email, otp, and timestamp."""
        self.email = email
        self.otp = otp
        self.timestamp = timestamp

    def to_dict(self):
        """Convert OTPStore object to dictionary for JSON response."""
        return {
            "id": self.id,
            "email": self.email,
            "otp": self.otp,
            "timestamp": self.timestamp.isoformat()  # Format timestamp as ISO string
        }


# -------------------------------------------- EMPLOYEE TABLE ----------------------------------------------------------
class Employee(Base):
    __tablename__ = 'employee'

    """
    Represents an employee in the company.

    Attributes:
        id (UUID): Unique identifier for the employee.
        first_name (str): Employee's first name.
        last_name (str): Employee's last name.
        emp_email (str): Unique email address of the employee.
        emp_num (str): Employee number.
        phone (str): Contact number of the employee.
        hire_date (Date): Date when the employee was hired.
        position (str): Employee's job position.
        salary (Decimal): Employee's salary.
        department (str): Department where the employee works.
        age (int): Employee's age.
        sex (str): Gender of the employee.
        blood_group (str): Blood group of the employee.
        height (Decimal): Employee's height in meters.
        weight (Decimal): Employee's weight in kilograms.
        address (str): Residential address of the employee.
        emergency_contact (str): Emergency contact number.
        nationality (str): Nationality of the employee.
        date_of_birth (Date): Employee's date of birth.
        marital_status (str): Employee's marital status.
        employment_status (str): Employee's employment status.
        insurance_number (str): Employee's insurance number.
        created_at (DateTime): Timestamp of when the record was created.
    """

    id = Column(UUID, primary_key=True, default=func.uuid_generate_v4())
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    emp_email = Column(String(150), nullable=False, unique=True)
    emp_num = Column(String, unique=True, nullable=False)
    phone = Column(String(15), nullable=True)
    hire_date = Column(Date, nullable=False)
    position = Column(String(50), nullable=True)
    salary = Column(Numeric(10, 2), nullable=True)
    department = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)
    blood_group = Column(String(3), nullable=True)
    height = Column(Numeric(5, 2), nullable=True)
    weight = Column(Numeric(5, 2), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String(15), nullable=True)
    nationality = Column(String(50), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    marital_status = Column(String(20), nullable=True)
    employment_status = Column(String(20), nullable=True)
    insurance_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship with HeavyProduct
    heavy_products = relationship("HeavyProduct", back_populates="employee")

    def to_dict(self):
        """Convert employee object to dictionary for JSON response."""
        return {
            "id": str(self.id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "emp_email": self.emp_email,
            "emp_num": self.emp_num,
            "phone": self.phone,
            "hire_date": self.hire_date.isoformat(),
            "position": self.position,
            "salary": str(self.salary) if self.salary is not None else None,
            "department": self.department,
            "age": self.age,
            "sex": self.sex,
            "blood_group": self.blood_group,
            "height": str(self.height) if self.height is not None else None,
            "weight": str(self.weight) if self.weight is not None else None,
            "address": self.address,
            "emergency_contact": self.emergency_contact,
            "nationality": self.nationality,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "marital_status": self.marital_status,
            "employment_status": self.employment_status,
            "insurance_number": self.insurance_number,
            "created_at": self.created_at.isoformat()
        }


# -------------------------------------------- HEAVY PRODUCTS TABLE ----------------------------------------------------
class HeavyProduct(Base):
    __tablename__ = 'heavy_products'

    """
    Represents heavy machinery products in the inventory.

    Attributes:
        id (UUID): Unique identifier for the heavy product.
        name (str): Name of the machinery product.
        type (str): Type of machinery (e.g., excavator, bulldozer).
        brand (str): Brand of the machinery.
        model (str): Model of the machinery.
        year_of_manufacture (int): Year the machinery was manufactured.
        price (decimal): Price of the machinery.
        weight (decimal): Weight of the machinery in kilograms.
        dimensions (str): Dimensions of the machinery.
        engine_type (str): Type of engine used in the machinery.
        horsepower (decimal): Horsepower of the machinery's engine.
        fuel_capacity (decimal): Fuel tank capacity in liters.
        operational_hours (int): Number of operational hours.
        warranty_period (int): Warranty period in months.
        status (str): Status of the machinery (available, sold, reserved).
        description (str): Description of the machinery.
        image_url (str): URL for the product image.
        created_at (datetime): Timestamp of when the record was created.
        updated_at (datetime): Timestamp of the last update.
        employee_id (UUID): Foreign key referencing the employee responsible for the machinery.
    """

    id = Column(UUID, primary_key=True, default=func.uuid_generate_v4())
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year_of_manufacture = Column(Integer, nullable=True)
    price = Column(Numeric(15, 2), nullable=False)
    weight = Column(Numeric(10, 2), nullable=False)
    dimensions = Column(String(50), nullable=True)
    engine_type = Column(String(100), nullable=True)
    horsepower = Column(Numeric(10, 2), nullable=True)
    fuel_capacity = Column(Numeric(10, 2), nullable=True)
    operational_hours = Column(Integer, nullable=True)
    warranty_period = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    employee_id = Column(UUID, ForeignKey('employee.id'), nullable=True)
    employee_name = Column(String, nullable=False)
    employee_num = Column(String, nullable=False)
    employee = relationship("Employee", back_populates="heavy_products")



    def to_dict(self):
        """Convert heavy product object to dictionary for JSON response."""
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type,
            "brand": self.brand,
            "model": self.model,
            "year_of_manufacture": self.year_of_manufacture,
            "price": str(self.price),
            "weight": str(self.weight),
            "dimensions": self.dimensions,
            "engine_type": self.engine_type,
            "horsepower": str(self.horsepower) if self.horsepower is not None else None,
            "fuel_capacity": str(self.fuel_capacity) if self.fuel_capacity is not None else None,
            "operational_hours": self.operational_hours,
            "warranty_period": self.warranty_period,
            "status": self.status,
            "description": self.description,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "employee_id": str(self.employee_id) if self.employee_id else None,
            "employee_name": self.employee.first_name + ' ' + self.employee.last_name if self.employee else None,
            "employee_num": self.employee.emp_num if self.employee else None
        }
