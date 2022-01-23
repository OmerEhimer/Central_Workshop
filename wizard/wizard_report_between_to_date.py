# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime

class WizardBetweenToDtae(models.TransientModel):

    _name = 'wizard.between.to.date'

    company_id = fields.Many2one('res.company', string='Maintenance',  required=True)
    start_date = fields.Date(string="Start Date" , required=True)
    end_date = fields.Date(string="End Date" , required=True)

    def _get_heigh_malfunctions(self, data):
        if not data : return
        max_malfunctions = data[0].malfunctions_type_id
        for m in data:
            if m.malfunctions_type_id.weight < max_malfunctions.weight :
                max_malfunctions = m.malfunctions_type_id
        return max_malfunctions
    
    def print_report_between(self):
        
        select_data = self.env['workshope.maintenance'].search([('company_id','=', self.company_id.id),('state','=','repaired')
        ,('request_date','>=', self.start_date),('request_date','<=', self.end_date)])
        for r in self :
            res = {
                    'start_date':r.start_date,
                    'end_date':r.end_date,
                    'company_ids' : r.company_id.name,
                }
            
            rows = []
            for r in select_data:
                rows.append({
                    'chassis': r.chassis_id.chassis,
                    'units_id': r.units_id.name,
                    'plate_number': r.plate_number,
                    'car_type':r.car_type,
                    'request_date': r.request_date,
                    'prodect_line':r.prodect_line,
                    'spairs' : " , ".join(s.product_id.name for s in select_data.prodect_line),
                    'type_malf' : self._get_heigh_malfunctions(select_data.malfunctions_lines).name,
                })
            res['rows'] = rows 
            return self.env.ref('Central_Workshop.print_between_to_date').report_action(self,data=res)

