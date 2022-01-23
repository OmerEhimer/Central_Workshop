# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime

class WizardMoveProduct(models.TransientModel):

    _name = 'wizard.move.product'

    stock_id = fields.Many2one('stock.location', string='Name Of Stock',  required=True)
    product_id = fields.Many2one('product.template', string="Product Name" , required=True)
    start_date = fields.Date(string="Start Date" , required=True)
    end_date = fields.Date(string="End Date" , required=True)

    def get_balance(self, product_id,stock_id,start_date):

            sql = '''
                    SELECT 
                        COALESCE(sum(product_qty),0) 
                     from 
                        stock_move
                    WHERE
                        product_id = %s
                        AND location_dest_id = %s
                        AND to_char(date_expected, 'YYYY-MM-DD') <= '%s' 
                    ''' %(product_id,stock_id,start_date)

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
                        AND to_char(date_expected, 'YYYY-MM-DD') <= '%s' 
                    ''' %(product_id,stock_id,start_date)

            self.env.cr.execute(sql)
            out_res = self.env.cr.fetchall()[0][0]

            
            
            balance = in_res - out_res
            return balance

    def print_move_product(self):

        select_data = self.env['stock.move'].search([('product_id','=', self.product_id.id),'|',('location_id','=', self.stock_id.id),('location_dest_id','=', self.stock_id.id) 
        ,('date_expected','>=', self.start_date),('date_expected','<=', self.end_date)]).read(['picking_id','date_expected','product_uom_qty','location_id','location_dest_id'])

        res = {
            'start_date' : self.start_date,
            'end_date' : self.end_date,
            'stock_id' : self.stock_id.id,
            'stock_name' : self.stock_id.name,
            'product_id' : self.product_id.name,
            'start_balance' : self.get_balance(self.product_id.id, self.stock_id.id, self.start_date),
            'end_balance' : self.get_balance(self.product_id.id, self.stock_id.id, self.end_date),
            'records' : select_data,
        }
        return self.env.ref('Central_Workshop.send_data_move_product').report_action(self,data=res)

