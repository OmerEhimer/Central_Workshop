# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime

class WizardExportImport(models.TransientModel):

    _name = 'wizard.export.import'

    stock_id = fields.Many2one('stock.location', string='Name Of Stock',  required=True)
    product_id = fields.Many2one('product.template', string="Product Name" , required=True)
    start_date = fields.Date(string="Start Date" , required=True)
    end_date = fields.Date(string="End Date" , required=True)

    
    def get_balance(self, product_id,stock_id,start_date,end_date):

        sql = '''
                SELECT 
                    COALESCE(sum(product_qty),0) 
                    from 
                    stock_move
                WHERE
                    product_id = %s
                    AND location_dest_id = %s
                    AND to_char(date_expected, 'YYYY-MM-DD') >= '%s' 
                    AND to_char(date_expected, 'YYYY-MM-DD') <= '%s' 
                ''' %(product_id,stock_id,start_date,end_date)

        self.env.cr.execute(sql)
        in_res = self.env.cr.fetchall()[0][0]

        sql = '''
                SELECT 
                    COALESCE(sum(product_qty),0) 
                    from 
                    stock_move
                WHERE
                    product_id = %s
                    AND location_id = %s
                    AND to_char(date_expected, 'YYYY-MM-DD') >= '%s' 
                    AND to_char(date_expected, 'YYYY-MM-DD') <= '%s' 
                ''' %(product_id,stock_id,start_date,end_date)

        self.env.cr.execute(sql)
        out_res = self.env.cr.fetchall()[0][0]

        balance = in_res - out_res
        
        print(">>>>>>>>>>>>>>>>>>>>>" , balance)
        
        return balance, in_res , out_res
    
    def print_export_import(self):
        result = self.get_balance(self.product_id.id, self.stock_id.id, self.start_date, self.end_date)
        res = {
            'start_date' : self.start_date,
            'end_date' : self.end_date,
            'stock_id' : self.stock_id.name,
            'product_id' : self.product_id.name,
            'barcode' :self.product_id.barcode,
            'balance' : result[0],
            'in_res' : result[1],
            'out_res' : result[2]
        }

        return self.env.ref('Central_Workshop.print_export_import').report_action(self,data=res)

