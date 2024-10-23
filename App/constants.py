REQUIRED_FIELDS_FOR_EMPLOYEE_TABLE = ['first_name', 'last_name', 'emp_email', 'emp_num', 'phone',
                                      'hire_date', 'position', 'salary', 'department',
                                      'age', 'sex', 'blood_group', 'height', 'weight',
                                      'address', 'emergency_contact', 'nationality',
                                      'date_of_birth', 'marital_status', 'employment_status',
                                      'insurance_number'
                                      ]

REQUIRED_FIELDS_FOR_HEAVY_MACHINERIES_TABLE = ['employee_id', 'name', 'type', 'brand', 'model',
                                               'year_of_manufacture', 'price', 'weight',
                                               'dimensions', 'engine_type', 'horsepower',
                                               'fuel_capacity', 'operational_hours',
                                               'warranty_period', 'status', 'description', 'image_url'
                                               ]

VALID_STATUSES = ['Available', 'Unavailable', 'Sold']

UPDATABLE_FIELDS = ['name', 'type', 'brand', 'model', 'year_of_manufacture', 'price', 'weight',
                    'dimensions', 'engine_type', 'horsepower', 'fuel_capacity', 'operational_hours',
                    'warranty_period', 'status', 'description', 'image_url', 'employee_id', 'employee_name',
                    'employee_num'
                    ]
