from odoo import api, fields, models
from odoo.tools.translate import _
from datetime import datetime , date
from odoo.exceptions import UserError


class WorkshopRequestSupply(models.Model):
    _name = 'request.supply'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Request To Supply Items'
    _rec_name = 'req_seq'
    
    @api.multi
    def print_finish_job(self):
        return self.env.ref('Central_Workshop.report_request_supply').report_action(self)

    req_seq = fields.Char(string='Request Sequence', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    
    destination_location = fields.Many2one('stock.location' , required=True , string='Destination Location' )
    source_location = fields.Many2one('stock.location', string='Source Location')
    company_id = fields.Many2one(string='Workshop', comodel_name='res.company', required=True, default=lambda self: self.env.user.company_id)

    request_date = fields.Date("Request Date",  default=date.today())
    prodect_line = fields.One2many(comodel_name="request.order.line", inverse_name="req_supp_id", string="Items")
    internal_note = fields.Text(" Notes") 
    income_pick_id = fields.Many2one('stock.picking', string="Incoming Shipment")
    outgoing_pick_id = fields.Many2one('stock.picking', string="Outgoing Shipment")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('check_availability', 'Check Availability'),
        ('approve', 'Approve'),
        ('done', 'Done'), ], string="Request Supply State" , track_visibility="always",required=True, default='draft')
    
    #this function for create sequence
    @api.model
    def create(self, vals):
        if vals.get('req_seq', _('New')) == _('New'):
           vals['req_seq'] = self.env['ir.sequence'].next_by_code('request.supply.sequence') or _('New')
        result = super(WorkshopRequestSupply, self).create(vals)
        return result
    
    
    def draft(self):
        for rec in self:
            for check_pro in rec.prodect_line: 
                if check_pro.req_supp_id:
                    self.state='confirm'
                    return True
        raise UserError(_("Please Choose Any product")) 
        
        
    def confirm(self):
        self.state='check_availability'
    
    def check_availability(self):    
        if self._check_availability():
            self.state='approve'
            
    def _check_availability(self):
        for lines in self.prodect_line :
            if lines.done_quantity > lines.qty_available or lines.done_quantity <= 0:
                raise UserError("You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.")
        return True
         
        
    #--------------------------------------------------#
    
    def create_pick(self,location,pick_type):
    
        location_model = self.env['stock.location']
        if pick_type == "outgoing" :
            source_location = location.id
            destination_location = location_model.search([('usage', '=', 'customer')])[0].id
            pick_type_id = self.env['stock.picking.type'].search([('code','=','outgoing'),('warehouse_id','=',location.company_id.warehouse_id.id)])[0].id
        else :
            destination_location = location.id
            source_location = location_model.search([('usage', '=', 'supplier')])[0].id
            pick_type_id = self.env['stock.picking.type'].search([('code','=','incoming'),('warehouse_id','=',location.company_id.warehouse_id.id)])[0].id
        
            
        move_model = self.env['stock.move']
        move_vals = []
        for line in self.prodect_line :
            move_vals.append((0,0,{
                    'product_id' : line.product_id.id,
                    'product_uom' : line.product_uom_id.id,
                    'product_uom_qty' : line.done_quantity,
                    'name' : '/' ,
                    'location_id' : source_location,
                    'location_dest_id' : destination_location, 
                }))
                # line.picked = True
        if move_vals : 
            picking_obj = self.env['stock.picking'].create({
                'picking_type_id' : pick_type_id,
                'location_id' : source_location,
                'location_dest_id' : destination_location, 
                'origin' : self.req_seq,
                'move_ids_without_package' : move_vals
            })
            picking_obj.action_confirm()
            picking_obj.action_assign()
            for move_line in picking_obj.move_line_ids:
                move_line.qty_done = move_line.product_uom_qty
            picking_obj.action_done()
            return picking_obj
        
            
    def approve(self):
       
        out_pick = self.create_pick(self.source_location, 'outgoing')
        print("out pick " , out_pick)
        in_pick = self.create_pick(self.destination_location, 'incoming')
        print("in pick " , in_pick)
        self.outgoing_pick_id = out_pick.id
        self.income_pick_id = in_pick.id 
        
        self.state='done'
        
#--------------------------------------------------#     incoming
    
  

# ---------- class for items line --------- #
class MaintenanceOrderLine(models.Model):
    """ Model for case stages. This models the main stages of a Maintenance Request management flow. """

    _name = 'request.order.line'
    _description = 'request supply Stage'

    product_id = fields.Many2one("product.template", string="Spare Name" ,required=True)
    product_uom_id = fields.Many2one("uom.uom", string="Product Uom" , required=True)
    quantity = fields.Float('Quantity', required=True)
    done_quantity = fields.Float('Done Quantity', required=True)
    req_supp_id = fields.Many2one("request.supply")    
    
    qty_available = fields.Float("On hand", related="product_id.qty_available")
    # picked= fields.Boolean(string='picked')
    
    @api.onchange('product_id')
    def onchange_product(self):
        category_id = self.product_id.uom_id.category_id.id
        return {
            'domain' : {
                'product_uom_id' : [('category_id', '=', category_id)]
            },
            'value' : {
                'product_uom_id' : False,
            }
        }

