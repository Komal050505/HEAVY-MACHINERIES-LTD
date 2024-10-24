import uuid
from datetime import datetime

import pytz
from sqlalchemy import Column, String, Integer, Numeric, DateTime, func, UUID, Text, ForeignKey, Date, \
    Float, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

Base = declarative_base()


# -------------------------------------------- OTP STORE TABLE ---------------------------------------------------------
class OTPStore(Base):
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
    __tablename__ = 'otp_store'

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
    """
    Represents an employee in the company.

    Attributes:
        emp_id (UUID): Unique identifier for the employee.
        emp_first_name (str): Employee's first name.
        emp_last_name (str): Employee's last name.
        emp_email (str): Unique email address of the employee.
        emp_num (str): Employee number.
        emp_phone (str): Contact number of the employee.
        emp_hire_date (Date): Date when the employee was hired.
        emp_position (str): Employee's job position.
        emp_salary (Decimal): Employee's salary.
        emp_department (str): Department where the employee works.
        emp_age (int): Employee's age.
        emp_sex (str): Gender of the employee.
        emp_blood_group (str): Blood group of the employee.
        emp_height (Decimal): Employee's height in meters.
        emp_weight (Decimal): Employee's weight in kilograms.
        emp_address (str): Residential address of the employee.
        emp_emergency_contact (str): Emergency contact number.
        emp_nationality (str): Nationality of the employee.
        emp_date_of_birth (Date): Employee's date of birth.
        emp_marital_status (str): Employee's marital status.
        emp_employment_status (str): Employee's employment status.
        emp_insurance_number (str): Employee's insurance number.
        emp_created_at (DateTime): Timestamp of when the record was created.
    """
    __tablename__ = 'employee'

    emp_id = Column(UUID, primary_key=True, default=func.uuid_generate_v4())
    emp_first_name = Column(String(100), nullable=False)
    emp_last_name = Column(String(100), nullable=False)
    emp_email = Column(String(150), nullable=False, unique=True)
    emp_num = Column(String, unique=True, nullable=False)
    emp_phone = Column(String(15), nullable=True)
    emp_hire_date = Column(Date, nullable=False)
    emp_position = Column(String(50), nullable=True)
    emp_salary = Column(Numeric(10, 2), nullable=True)
    emp_department = Column(String(50), nullable=True)
    emp_age = Column(Integer, nullable=True)
    emp_sex = Column(String(10), nullable=True)
    emp_blood_group = Column(String(3), nullable=True)
    emp_height = Column(Numeric(5, 2), nullable=True)
    emp_weight = Column(Numeric(5, 2), nullable=True)
    emp_address = Column(Text, nullable=True)
    emp_emergency_contact = Column(String(15), nullable=True)
    emp_nationality = Column(String(50), nullable=True)
    emp_date_of_birth = Column(Date, nullable=True)
    emp_marital_status = Column(String(20), nullable=True)
    emp_employment_status = Column(String(20), nullable=True)
    emp_insurance_number = Column(String(50), nullable=True)
    emp_created_at = Column(DateTime, server_default=func.now())

    # Relationship with HeavyProduct
    heavy_products = relationship("HeavyProduct", back_populates="employee")

    def to_dict(self):
        """Convert employee object to dictionary for JSON response."""
        return {
            "emp_id": str(self.emp_id),
            "emp_first_name": self.emp_first_name,
            "emp_last_name": self.emp_last_name,
            "emp_email": self.emp_email,
            "emp_num": self.emp_num,
            "emp_phone": self.emp_phone,
            "emp_hire_date": self.emp_hire_date.isoformat(),
            "emp_position": self.emp_position,
            "emp_salary": str(self.emp_salary) if self.emp_salary is not None else None,
            "emp_department": self.emp_department,
            "emp_age": self.emp_age,
            "emp_sex": self.emp_sex,
            "emp_blood_group": self.emp_blood_group,
            "emp_height": str(self.emp_height) if self.emp_height is not None else None,
            "emp_weight": str(self.emp_weight) if self.emp_weight is not None else None,
            "emp_address": self.emp_address,
            "emp_emergency_contact": self.emp_emergency_contact,
            "emp_nationality": self.emp_nationality,
            "emp_date_of_birth": self.emp_date_of_birth.isoformat() if self.emp_date_of_birth else None,
            "emp_marital_status": self.emp_marital_status,
            "emp_employment_status": self.emp_employment_status,
            "emp_insurance_number": self.emp_insurance_number,
            "emp_created_at": self.emp_created_at.isoformat()
        }


# -------------------------------------------- HEAVY PRODUCTS TABLE ----------------------------------------------------
class HeavyProduct(Base):
    """
    Represents heavy machinery products in the inventory.

    Attributes:
        heavy_product_id (UUID): Unique identifier for the heavy product.
        heavy_product_name (str): Name of the machinery product.
        heavy_product_type (str): Type of machinery (e.g., excavator, bulldozer).
        heavy_product_brand (str): Brand of the machinery.
        heavy_product_model (str): Model of the machinery.
        heavy_product_year_of_manufacture (int): Year the machinery was manufactured.
        heavy_product_price (decimal): Price of the machinery.
        heavy_product_weight (decimal): Weight of the machinery in kilograms.
        heavy_product_dimensions (str): Dimensions of the machinery.
        heavy_product_engine_type (str): Type of engine used in the machinery.
        heavy_product_horsepower (decimal): Horsepower of the machinery's engine.
        heavy_product_fuel_capacity (decimal): Fuel tank capacity in liters.
        heavy_product_operational_hours (int): Number of operational hours.
        heavy_product_warranty_period (int): Warranty period in months.
        heavy_product_status (str): Status of the machinery (available, sold, reserved).
        heavy_product_description (str): Description of the machinery.
        heavy_product_image_url (str): URL for the product image.
        heavy_product_created_at (datetime): Timestamp of when the record was created.
        heavy_product_updated_at (datetime): Timestamp of the last update.
        employee_id (UUID): Foreign key referencing the employee responsible for the machinery.
        employee_name (str): Name of the employee responsible for the product.
        employee_num (str): Employee number of the employee responsible for the product.
    """
    __tablename__ = 'heavy_products'

    heavy_product_id = Column(UUID, primary_key=True, default=func.uuid_generate_v4())
    heavy_product_name = Column(String(255), nullable=False)
    heavy_product_type = Column(String(100), nullable=False)
    heavy_product_brand = Column(String(100), nullable=False)
    heavy_product_model = Column(String(100), nullable=False)
    heavy_product_year_of_manufacture = Column(Integer, nullable=True)
    heavy_product_price = Column(Numeric(15, 2), nullable=False)
    heavy_product_weight = Column(Numeric(10, 2), nullable=False)
    heavy_product_dimensions = Column(String(50), nullable=True)
    heavy_product_engine_type = Column(String(100), nullable=True)
    heavy_product_horsepower = Column(Numeric(10, 2), nullable=True)
    heavy_product_fuel_capacity = Column(Numeric(10, 2), nullable=True)
    heavy_product_operational_hours = Column(Integer, nullable=True)
    heavy_product_warranty_period = Column(Integer, nullable=True)
    heavy_product_status = Column(String(20), nullable=False)
    heavy_product_description = Column(Text, nullable=True)
    heavy_product_image_url = Column(String(255), nullable=True)
    heavy_product_created_at = Column(DateTime, server_default=func.now())
    heavy_product_updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    employee_id = Column(UUID, ForeignKey('employee.emp_id'), nullable=True)
    employee_name = Column(String, nullable=False)
    employee_num = Column(String, nullable=False)

    employee = relationship("Employee", back_populates="heavy_products")
    opportunities = relationship('HeavyMachineryOpportunity', backref='heavy_products', lazy=True)

    def to_dict(self):
        """Convert heavy product object to dictionary for JSON response."""
        return {
            "heavy_product_id": str(self.heavy_product_id),
            "heavy_product_name": self.heavy_product_name,
            "heavy_product_type": self.heavy_product_type,
            "heavy_product_brand": self.heavy_product_brand,
            "heavy_product_model": self.heavy_product_model,
            "heavy_product_year_of_manufacture": self.heavy_product_year_of_manufacture,
            "heavy_product_price": str(self.heavy_product_price),
            "heavy_product_weight": str(self.heavy_product_weight),
            "heavy_product_dimensions": self.heavy_product_dimensions,
            "heavy_product_engine_type": self.heavy_product_engine_type,
            "heavy_product_horsepower": str(
                self.heavy_product_horsepower) if self.heavy_product_horsepower is not None else None,
            "heavy_product_fuel_capacity": str(
                self.heavy_product_fuel_capacity) if self.heavy_product_fuel_capacity is not None else None,
            "heavy_product_operational_hours": self.heavy_product_operational_hours,
            "heavy_product_warranty_period": self.heavy_product_warranty_period,
            "heavy_product_status": self.heavy_product_status,
            "heavy_product_description": self.heavy_product_description,
            "heavy_product_image_url": self.heavy_product_image_url,
            "heavy_product_created_at": self.heavy_product_created_at.isoformat(),
            "heavy_product_updated_at": self.heavy_product_updated_at.isoformat(),
            "employee_id": str(self.employee_id) if self.employee_id else None,
            "employee_name": self.employee.emp_first_name + ' ' + self.employee.emp_last_name if self.employee else None,
            "employee_num": self.employee.emp_num if self.employee else None,

        }


# --------------------------------------- HEAVY MACHINERIES OPPORTUNITY TABLE ------------------------------------------


class HeavyMachineryOpportunity(Base):
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
    __tablename__ = 'heavy_machinery_opportunities'

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
    employee_id = Column(UUID, ForeignKey('employee.emp_id'), nullable=True)
    product_id = Column(UUID, ForeignKey('heavy_products.heavy_product_id'),
                        nullable=False)  # Foreign Key to HeavyProduct
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
            "employee_name": f"{self.employee.emp_first_name} {self.employee.emp_last_name}" if self.employee else None,
            "employee_num": self.employee.emp_num if self.employee else None,
            "currency_conversions": format_currency_conversions(),
            'product_id': str(self.product_id) if self.product_id else None,
            'product_name': self.product_name,
            'product_brand': self.product_brand,
            'product_model': self.product_model,
            'product_image_url': self.product_image_url,
        }


class HeavyMachineryCustomer(Base):
    """
    HeavyMachineryCustomer model represents customers of heavy machinery dealerships.
    Each customer is associated with an opportunity, a dealer, and an employee.

    Attributes:
        customer_id (UUID): Unique identifier for the customer.
        customer_name (str): The name of the customer.
        customer_contact_info (str): Contact information for the customer (e.g., phone, email).
        customer_address (str): Address of the customer.
        opportunity_id (UUID): Foreign key to the opportunity that led to the customer conversion.
        dealer_id (UUID): Foreign key to the dealer responsible for managing the customer.
        employee_id (UUID): Foreign key to the employee managing the customer's interactions.
        customer_status (str): Status of the customer (e.g., new, contacted, in-progress, closed).
        customer_comments (str): Dealer's comments or notes about the customer.
        customer_feedback (str): Feedback provided by the dealer about the customer’s interaction or potential.
        customer_created_at (datetime): Timestamp when the customer was created.
        customer_updated_at (datetime): Timestamp when the customer record was last updated.
        customer_last_interaction (datetime): Timestamp of the last recorded interaction with the customer.
    """

    __tablename__ = 'heavy_machinery_customers'

    customer_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_name = Column(String(255), nullable=False)
    customer_contact_info = Column(Text)  # Stores customer contact information like email, phone, etc.
    customer_address = Column(Text)  # Stores customer address
    opportunity_id = Column(PGUUID(as_uuid=True), ForeignKey('heavy_machinery_opportunities.opportunity_id'))
    dealer_id = Column(PGUUID(as_uuid=True), ForeignKey('heavy_machineries_dealer.dealer_id'))
    employee_id = Column(PGUUID(as_uuid=True), ForeignKey('employee.emp_id'))
    customer_status = Column(String(50), default='new')  # Status can be new, contacted, in-progress, closed
    customer_comments = Column(Text)  # Comments by the dealer regarding customer interaction
    customer_feedback = Column(Text)  # Feedback provided by the dealer
    customer_created_at = Column(TIMESTAMP, server_default=func.now())  # Time when customer was created
    customer_updated_at = Column(TIMESTAMP, server_default=func.now(),
                                 onupdate=func.now())  # Time when customer was last updated
    customer_last_interaction = Column(TIMESTAMP)  # Last interaction time with the customer

    def to_dict(self):
        """
        Converts the HeavyMachineryCustomer object to a dictionary representation.

        :return: dict containing customer data.
        """
        return {
            "customer_id": str(self.customer_id),
            "customer_name": self.customer_name,
            "customer_contact_info": self.customer_contact_info,
            "customer_address": self.customer_address,
            "opportunity_id": str(self.opportunity_id) if self.opportunity_id else None,
            "dealer_id": str(self.dealer_id) if self.dealer_id else None,
            "employee_id": str(self.employee_id) if self.employee_id else None,
            "customer_status": self.customer_status,
            "customer_comments": self.customer_comments,
            "customer_feedback": self.customer_feedback,
            "customer_created_at": self.customer_created_at.isoformat() if self.customer_created_at else None,
            "customer_updated_at": self.customer_updated_at.isoformat() if self.customer_updated_at else None,
            "customer_last_interaction": self.customer_last_interaction.isoformat() if self.customer_last_interaction else None
        }

    def __repr__(self):
        """
        String representation of the HeavyMachineryCustomer object.

        :return: str with basic customer details.
        """
        return f"<HeavyMachineryCustomer(customer_id={self.customer_id}, customer_name={self.customer_name})>"
