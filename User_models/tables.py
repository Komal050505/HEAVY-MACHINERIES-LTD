import uuid
from datetime import datetime

import pytz
from sqlalchemy import Column, String, Integer, Numeric, DateTime, func, UUID, Text, ForeignKey, Date, \
    Float
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


# -------------------------------------------- ACCOUNTS TABLE ---------------------------------------------------------

class Account(Base):
    """
    SQLAlchemy ORM class representing the 'heavy_machineries_accounts' table.

    This table stores customer account details like account_id and account_name.
    """
    __tablename__ = 'heavy_machineries_accounts'

    account_id = Column("account_id", String(100), primary_key=True)  # Using First 3 letters of account name +
    # 4 random digits for manually created at the time of account creation, not in create new customer API

    account_name = Column("account_name", String, nullable=False)

    def account_serialize_to_dict(self):
        """
        Converts the Account object into a dictionary.
        """
        return {
            'account_id': self.account_id,
            'account_name': self.account_name
        }


# -------------------------------------------- HEAVY PRODUCTS DEALER TABLE ---------------------------------------------------------
class HeavyMachineriesDealer(Base):
    """
    This table stores dealer information like dealer ID, code, and opportunity owner.
    """
    __tablename__ = 'heavy_machineries_dealer'

    dealer_id = Column("dealer_id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dealer_code = Column("dealer_code", String, nullable=False)
    opportunity_owner = Column("opportunity_owner", String, nullable=False)

    def dealer_serialize_to_dict(self):
        """
        Converts the HeavyProductsDealer object into a dictionary.
        """
        return {
            'dealer_id': self.dealer_id,
            'dealer_code': self.dealer_code,
            'opportunity_owner': self.opportunity_owner
        }

    opportunities = relationship("HeavyMachineryOpportunity", back_populates="dealer")


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
    opportunities = relationship('HeavyMachineryOpportunity', backref='heavy_product', lazy=True)

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
            "employee_num": self.employee.emp_num if self.employee else None,

        }


# --------------------------------------- HEAVY MACHINERIES OPPORTUNITY TABLE ------------------------------------------


class HeavyMachineryOpportunity(Base):
    __tablename__ = 'heavy_machinery_opportunities'

    """
    Represents opportunities related to heavy machinery.

    Attributes:
        opportunity_id (UUID): Unique identifier for the opportunity.
        opportunity_name (str): Name of the opportunity.
        account_name (str): Name of the account associated with the opportunity.
        close_date (datetime): Expected closing date of the opportunity.
        amount (decimal): Potential revenue from the opportunity.
        description (str): Description of the opportunity.
        dealer_id (UUID): Foreign key referencing the dealer.
        dealer_code (str): Code associated with the dealer.
        stage (str): Current stage of the opportunity.
        probability (int): Probability of closing the opportunity (in percentage).
        next_step (str): Next steps to move the opportunity forward.
        created_date (datetime): Timestamp of when the opportunity was created.
        amount_in_words (str): The amount in words.
        usd (float): US Dollars.
        aus (float): Australian Dollars.
        cad (float): Canadian Dollars.
        jpy (float): Japanese Yen.
        eur (float): Euros.
        gbp (float): British Pounds.
        cny (float): Chinese Yuan.
    """

    opportunity_id = Column("opportunity_id", String, primary_key=True, default=lambda: str(uuid.uuid1()))
    opportunity_name = Column("opportunity_name", String, nullable=False)
    account_name = Column("account_name", String, nullable=False)
    close_date = Column("close_date", DateTime, nullable=False)
    amount = Column("amount", Float, nullable=False)
    description = Column("description", String)
    dealer_id = Column("dealer_id", String, ForeignKey('heavy_machineries_dealer.dealer_id'), nullable=False)
    dealer_code = Column("dealer_code", String, nullable=False)
    stage = Column("stage", String, nullable=False)
    probability = Column("probability", Integer)
    next_step = Column("next_step", String)
    created_date = Column("created_date", DateTime, nullable=False,
                          default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    employee_id = Column(UUID, ForeignKey('employee.id'), nullable=True)
    product_id = Column(UUID, ForeignKey('heavy_products.id'), nullable=False)  # Foreign Key to HeavyProduct
    product_name = Column(String, nullable=False)
    product_brand = Column(String, nullable=False)
    product_model = Column(String, nullable=False)
    product_image_url = Column(String, nullable=True)

    # New currency columns
    amount_in_words = Column("amount_in_words", String)
    usd = Column("usd", Float)  # US Dollars
    aus = Column("aus", Float)  # Australian Dollars
    cad = Column("cad", Float)  # Canadian Dollars
    jpy = Column("jpy", Float)  # Japanese Yen
    eur = Column("eur", Float)  # Euros
    gbp = Column("gbp", Float)  # British Pounds
    cny = Column("cny", Float)  # Chinese Yuan

    # Relationships
    dealer = relationship("HeavyMachineriesDealer", back_populates="opportunities")
    employee = relationship("Employee")  # Relationship to Employee class
    product = relationship("HeavyProduct", back_populates="opportunities")  # New relationship to HeavyProduct

    def serialize_to_dict(self):
        """
        Serialize the Opportunity instance to a dictionary with formatted dates and currency conversions.
        :return: dict
        """

        def format_datetime(dt):
            """Format datetime to 12-hour format with AM/PM"""
            return dt.strftime("%I:%M %p, %B %d, %Y") if dt else None

        def format_currency_conversions():
            """Format currency conversions into a readable string"""
            currencies = {
                'USD': self.usd,
                'AUD': self.aus,
                'CAD': self.cad,
                'JPY': self.jpy,
                'EUR': self.eur,
                'GBP': self.gbp,
                'CNY': self.cny
            }
            return '\n'.join(
                f"{currency}: {value if value is not None else 'None'}" for currency, value in currencies.items()
            )

        return {
            'opportunity_id': self.opportunity_id,
            'opportunity_name': self.opportunity_name,
            'account_name': self.account_name,
            'close_date': format_datetime(self.close_date) if self.close_date else None,
            'amount': self.amount,
            'amount_in_words': self.amount_in_words,
            'description': self.description,
            'dealer_id': self.dealer_id,
            'dealer_code': self.dealer_code,
            'stage': self.stage,
            'probability': self.probability,
            'next_step': self.next_step,
            'created_date': format_datetime(self.created_date) if self.created_date else None,
            "employee_id": str(self.employee_id) if self.employee_id else None,
            "employee_name": f"{self.employee.first_name} {self.employee.last_name}" if self.employee else None,
            "employee_num": self.employee.emp_num if self.employee else None,
            "currency_conversions": format_currency_conversions(),
            'product_id': str(self.product_id) if self.product_id else None,
            'product_name': self.product_name,
            'product_brand': self.product_brand,
            'product_model': self.product_model,
            'product_image_url': self.product_image_url,
        }
