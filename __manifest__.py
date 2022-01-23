# -*- coding: utf-8 -*-
{
    'name': "central_workshope",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','sale','stock'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
       
        # ------------------------------------------#
        'views/workshope_maintenance.xml',
        'views/workshope_malfunctions.xml',
        'views/workshope_malfunctions_type.xml',
        'views/workshope_cars_model.xml',
        'views/workshope_section.xml',
        'views/workshope_units.xml',
        'views/workshope_employee.xml',
        'views/rsf_weapon.xml',
        'views/dashboard.xml',
        'views/style_css.xml',
        'views/workshope_cars.xml',
        'views/workshope_request_to_supply_items.xml',

        # ------------------------------------------#
        'data/sequence.xml',
        # 'data/stage.xml',
        #-------------------------------------------#
        'reports/workshope_job_report.xml',
        'reports/workshope_finish_job.xml',
        'reports/workshope_inventory_esper.xml',
        'reports/report_between_to_date.xml',
        'reports/workshope_repot_move_product.xml',
        'reports/workshope_repot_export_import.xml',
        'reports/workshope_request_supply.xml',
        'reports/report.xml',

        #-------------------------------------------#
        'wizard/wizard_report_between_to_date.xml',
        'wizard/wizard_report_move_product.xml',
        'wizard/wizard_report_export_import.xml',
        
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
