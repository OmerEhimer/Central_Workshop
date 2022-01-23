from odoo import api, fields, models ,tools
from odoo.tools.translate import _
from odoo.exceptions import ValidationError,Warning
from datetime import datetime , date
from logging import warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.fields import Date

class Location(models.Model) :
    _inherit = 'stock.location'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """ search full name and barcode """
        args = args or []
        maintenance_id = self.env.context.get('maintenance_id', False)
        if maintenance_id :
            maintenance_obj = self.env.get('workshope.maintenance').browse(maintenance_id)
            parent_location_id = maintenance_obj.company_id.warehouse_id.view_location_id.id
            args += [('location_id', '=', parent_location_id)]
        return super(Location, self)._name_search(name, args, operator,limit,name_get_uid)

class WorkshopeMaintenance(models.Model):
    _name = 'workshope.maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name='maintenance_seq'
    _description = 'Maintenance '
    _order = "maintenance_seq desc"


    @api.multi
    def print_job(self):
        self.state='in_check'
        self.chassis_id.state='in_service'
        return self.env.ref('Central_Workshop.job_report_data').report_action(self)

    @api.multi
    def print_finish_job(self):
        return self.env.ref('Central_Workshop.report_finish_job').report_action(self)

    @api.multi
    def print_in_inventory(self):
        return self.env.ref('Central_Workshop.report_in_inventory').report_action(self)
                


    maintenance_seq = fields.Char(string='Job ID', required=True, copy=False, readonly=True,
    index=True, default=lambda self: _('New'))
    request_date = fields.Date("Request Date",  default=date.today())
    maintenance_type = fields.Selection([
        ('preventive', 'Syclic'),
        ('corrective', 'Corrective'),
    ], string="Maintenance Type")
    
    priority = fields.Selection([
        ('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')
    ], string="Priority")
    scheduled_Date = fields.Date(string="Scheduled Date")
    
    location_id = fields.Many2one('stock.location' , string='Location')
    chassis_id = fields.Many2one('workshope.cars',string='Chassis',required=True,track_visibility="always",)
    plate_number = fields.Char(string='Plate Number',track_visibility="always", related='chassis_id.plate_number' )
    fuel_type = fields.Selection(string="Feul Type", related="chassis_id.fuel_type")
    transmision = fields.Selection(string="Transmision", related="chassis_id.transmision")
    units_id = fields.Many2one('workshope.units',string="Units", track_visibility="always",related='chassis_id.units_id')
    rece_of = fields.Char(string='Rece Officer',track_visibility="always",related='chassis_id.rece_of')

    category = fields.Selection(string="Catogory", related="chassis_id.category")
    officer = fields.Selection(string="Rank", related="chassis_id.officer")
    warrant_officer = fields.Selection(string="Warrant Officer", related="chassis_id.warrant_officer")
    phone = fields.Char(string='Phone', track_visibility="always" ,related='chassis_id.phone')  
    car_type = fields.Selection([
        ('private', 'Private'),
        ('combative', 'Combative'),
        ('administrative', 'Administrative'),
    ], string="Car Type" , track_visibility="always",required=True,related='chassis_id.car_type' ) 
    state = fields.Selection([
        ('new_request', 'New Request'),
        ('in_check', 'In Check'),
        ('wait_confirm', 'Wait Confirm'),
        ('confirmation', 'Confirmation'),
        ('inventory', 'Inventory'),
        ('in_progress', 'In Progress'),
        ('repaired', 'Repaired'),
        ('scrap', 'Scrap'),
       
    ], string="Job State" , track_visibility="always",required=True,default='new_request') 
    num_signal = fields.Char(string='Number Sig',track_visibility="always",required=True)  

    user_id = fields.Many2one('res.users',string="User",readonly="1",default=lambda self:self.env.user)
    company_id = fields.Many2one(string='Maintenance', comodel_name='res.company',readonly="1", required=True, default=lambda self: self.env.user.company_id)
    month = fields.Integer(string='Month', track_visibility="always",)
    year = fields.Integer(string='Year', track_visibility="always",)
    

    malfunctions_lines = fields.Many2many("workshoe.malfunctions" ,string="Malfunctions ")
    emp_line = fields.One2many(comodel_name="employee.line", inverse_name="maintenane_id",string="Employee Name")
    prodect_line = fields.One2many(comodel_name="maintenance.order.line", inverse_name="maintenance_id", string="Items")
    duration = fields.Float(help="Duration in hours and minutes.")
    color = fields.Integer('Color Index')
    kanban_state = fields.Selection([('normal', 'In Progress'), ('blocked', 'Blocked'), ('done', 'Ready for next stage')],
            string='Kanban State', required=True, default='normal', track_visibility='onchange')

    @api.model
    def create(self, vals):
        if vals.get('maintenance_seq', _('New')) == _('New'):
                vals['maintenance_seq'] = self.env['ir.sequence'].next_by_code('workshope.maintenance.sequence') or _('New')
        result = super(WorkshopeMaintenance, self).create(vals)
        return result
              
    @api.multi
    @api.constrains('phone')
    def _check_phone(self):
        for rec in self:
            if rec.phone and len(rec.phone) != 10:
                raise ValidationError(_("Invalid Phone Number..."))
        return True  


    # def print_job(self):
    #     self.state='in_check'

    def wait_confirm(self):
        self.state='wait_confirm'
    
    def confirm(self):
        self.state='confirmation'
#--------------------------------------------------#
    
    def inventory(self):
        # if not self.company_id.warehouse_id : raise Use 
        pick_type_id = self.env['stock.picking.type'].search([('code','=','outgoing'),('warehouse_id','=',self.company_id.warehouse_id.id)])[0].id
        location_model = self.env['stock.location']
        location_id = self.location_id.id 
        location_dest_id = location_model.search([('usage', '=', 'customer')])[0].id
        move_model = self.env['stock.move']
        move_vals = []
        for line in self.prodect_line :
            if not line.picked :
                move_vals.append((0,0,{
                    'product_id' : line.product_id.id,
                    'product_uom' : line.product_uom_id.id,
                    'product_uom_qty' : line.quantity,
                    'name' : '/' ,
                    'location_id' : location_id,
                    'location_dest_id' : location_dest_id, 
                }))
                line.picked = True
        if move_vals : 
            picking_obj = self.env['stock.picking'].create({
                'picking_type_id' : pick_type_id,
                'location_id' : location_id,
                'location_dest_id' : location_dest_id,
                'origin' : self.maintenance_seq,
                'move_ids_without_package' : move_vals
            })
            picking_obj.action_confirm()
            picking_obj.action_assign()

#--------------------------------------------------#

    def repaired(self):
        for rec in self:
            for line in rec.emp_line: 
                if line.emp_id:
                    self.state='repaired'   
                    return True
        raise Warning(_("Please Write Report"))

        
    def back_one(self):
        self.state='new_request'
        
    def scrap(self):
            self.state='scrap'
            self.chassis_id.state='out_service'

    def back_tow(self):
        self.state='in_progress'

    def new_request(self):
        self.state='new_request'

    def action_inventory(self):
        
        #if self.message_main_attachment_id.id is False:
            #raise Warning(_("الرجاء ارفاق الإشارة لصيانة للمركبة"))
        #else:
            self.state='inventory'



  
# ---------- class for items line --------- #
class MaintenanceOrderLine(models.Model):
    """ Model for case stages. This models the main stages of a Maintenance Request management flow. """

    _name = 'maintenance.order.line'
    _description = 'Maintenance Stage'

    product_id = fields.Many2one("product.template", string="Spare Name")
    default_code = fields.Char("Internal Referance", related="product_id.default_code")
    # categ_id = fields.Selection('Catogrey', related="product_id.categ_id")
    product_uom_id = fields.Many2one("uom.uom", string="Product Uom")
    p_type = fields.Selection('Price', related="product_id.type")
    qty_available = fields.Float("On hand", related="product_id.qty_available")
    quantity = fields.Float('Quantity', required=True)
    maintenance_id = fields.Many2one("workshope.maintenance")
    picked = fields.Boolean(string='Picking')
    
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
    


# -- Employee line for one 2 many field -- #

class EmployeeLine(models.Model):
    _name = 'employee.line'
    _description = ''

    emp_id = fields.Many2one('workshope.employee',string="Employee Name", required=True,track_visibility="always")
    section_id = fields.Many2one('workshope.section',string="Section", related="emp_id.section_ids")
    last_result = fields.Text(string='End Report',track_visibility='always')
    star_date = fields.Datetime("Reseved Date") 
    end_date = fields.Datetime("Delevery Date")
    maintenane_id = fields.Many2one('workshope.maintenance', string="Maintenane ID")


class StockTransferWiz(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        res = super(StockTransferWiz, self).process()
        for p in self.pick_ids :
            origin = p.origin
            self.env.get('workshope.maintenance').search([('maintenance_seq', '=', origin)]).write({'state' : 'in_progress'})
        return res


# class ResCompany(models.Model):
#     _inherit = 'res.company' 


class InheritCompany(models.Model):
    _inherit = 'res.company'    

    warehouse_id = fields.Many2one('stock.warehouse' , string="Warehouse")        
