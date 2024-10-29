REQUIRED_FIELDS_FOR_EMPLOYEE_TABLE = ['emp_first_name',
                                      'emp_last_name',
                                      'emp_email',
                                      'emp_num',
                                      'emp_phone',
                                      'emp_hire_date',
                                      'emp_position',
                                      'emp_salary',
                                      'emp_department',
                                      'emp_age',
                                      'emp_sex',
                                      'emp_blood_group',
                                      'emp_height',
                                      'emp_weight',
                                      'emp_address',
                                      'emp_emergency_contact',
                                      'emp_nationality',
                                      'emp_date_of_birth',
                                      'emp_marital_status',
                                      'emp_employment_status',
                                      'emp_insurance_number'
                                      ]

REQUIRED_FIELDS_FOR_HEAVY_MACHINERIES_TABLE = ['employee_id',
                                               'heavy_product_name',
                                               'heavy_product_type',
                                               'heavy_product_brand',
                                               'heavy_product_model',
                                               'heavy_product_year_of_manufacture',
                                               'heavy_product_price',
                                               'heavy_product_weight',
                                               'heavy_product_dimensions',
                                               'heavy_product_engine_type',
                                               'heavy_product_horsepower',
                                               'heavy_product_fuel_capacity',
                                               'heavy_product_operational_hours',
                                               'heavy_product_warranty_period',
                                               'heavy_product_status',
                                               'heavy_product_description',
                                               'heavy_product_image_url'
                                               ]

VALID_STATUSES = ['Available', 'Unavailable', 'Sold']

UPDATABLE_FIELDS = ['heavy_product_name',
                    'heavy_product_type',
                    'heavy_product_brand',
                    'heavy_product_model',
                    'heavy_product_year_of_manufacture',
                    'heavy_product_price',
                    'heavy_product_weight',
                    'heavy_product_dimensions',
                    'heavy_product_engine_type',
                    'heavy_product_horsepower',
                    'heavy_product_fuel_capacity',
                    'heavy_product_operational_hours',
                    'heavy_product_warranty_period',
                    'heavy_product_status',
                    'heavy_product_description',
                    'heavy_product_image_url',
                    'employee_id',
                    'employee_name',
                    'employee_num'
                    ]

REQUIRED_FIELDS_FOR_CUSTOMER_CREATION = ['customer_name',
                                         'customer_contact_info',
                                         'customer_address',
                                         'opportunity_id',
                                         'dealer_id',
                                         'employee_id'
                                         ]

