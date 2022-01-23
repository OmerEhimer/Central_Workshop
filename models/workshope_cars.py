from odoo import api, fields, models ,tools
from odoo.tools.translate import _
from odoo.exceptions import ValidationError,Warning
from datetime import date, datetime
from logging import warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.fields import Date

class WorkshopeCars(models.Model):
    _name = 'workshope.cars'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name='chassis'
    _description = 'Cars Form'
    _order = "cars_seq desc"

    cars_seq = fields.Char(string='Car Sequence', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'))
    #==========================================================================================
    chassis = fields.Char(string='Chassis',required=True,track_visibility="always")
    machine_no = fields.Char("Machine No",  track_visibility="always")
    plate_number = fields.Char(string='Plate Number',track_visibility="always")  
    units_id = fields.Many2one('workshope.units',string="Units",track_visibility="always") 
    #==========================================================================================
    model_id = fields.Many2one('workshope.cars.model','Model',track_visibility="onchange", help='Model of the vehicle')
    brand_id = fields.Many2one('fleet.vehicle.model.brand', 'Brand', related="model_id.brand_id", store=True, readonly=False)
    image_medium = fields.Binary(related='brand_id.image_medium', string="Logo (medium)", readonly=False)
    #========================================================================================================
    form_date = fields.Datetime(string='Date')
    color = fields.Integer('Color Index')

    category = fields.Selection([
        ('1', 'ضابط'),
        ('2', 'ضابط صف/جندي'),

    ], string="Cattegory" , track_visibility="always", )    
    officer = fields.Selection([
        ('1', 'فريق اول'),
        ('2', 'فريق'),
        ('3', 'لواء'),
        ('4', 'عميد'),
        ('5', 'عقيد'),
        ('6', 'مقدم'),
        ('7', 'رائد'),
        ('8', 'نقيب'),
        ('9', 'م.أول'),
        ('10', 'ملازم'),
    ], string="Officer" , track_visibility="always",)
    
    warrant_officer = fields.Selection([
        ('1', 'مساعد'),
        ('2', 'ر.أول'),
        ('3', 'رقيب'),
        ('4', 'عريف'),
        ('5', 'و.عريف'),
        ('6', 'جندي'),
        ('7', 'متعاقد'),
    ], string="Warrant Officer" , track_visibility="always",)
    
    car_type = fields.Selection([
        ('private', 'Private'),
        ('combative', 'Combative'),
        ('administrative', 'Administrative'),

    ], string="Car Type" , track_visibility="always",default='private' ) 
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_service', 'In Service'),
        ('out_service', 'Out Service'),

    ],string='State',  readonly=True, default='draft',) 
    fuel_type = fields.Selection([
        ('jazz', 'Jazz'),
        ('petrol', 'Petrol')
    ], string="Fuel Type")
    transmision = fields.Selection([
        ('manueal', 'Manueal'),
        ('automatic', 'Automatic'),
    ], string="Transnision" )
    #==========================================================================================
    rece_of = fields.Char(string='Rece Officer',track_visibility="always",) 
    card_no = fields.Char(string='Card NO', track_visibility="always")
    phone = fields.Char(string='Phone', track_visibility="always")
    location = fields.Char(string='Location', track_visibility="always")
    user_id = fields.Many2one('res.users',string="User",readonly="1",default=lambda self:self.env.user)
    company_id = fields.Many2one(string='My Company', comodel_name='res.company',readonly="1", default=lambda self: self.env.user.company_id)
    convertFormDate  = fields.Date(string='Date',track_visibility="always",store=True,)
    #==========================================================================================
    whay_out = fields.Text(string='Whay Out Service',track_visibility='always') 
    active = fields.Boolean(string="Active", default="True")
    maintenance_count = fields.Integer(compute="get_maintenance_count")
    #==========================================================================================
    weapon_line_id = fields.One2many(comodel_name="rsf.weapon.line", inverse_name="car_id", string="Weapon")

    @api.model
    def create(self, vals):
        if vals.get('cars_seq', _('New')) == _('New'):
                vals['cars_seq'] = self.env['ir.sequence'].next_by_code('workshope.cars.sequence') or _('New')
        result = super(WorkshopeCars, self).create(vals)
        return result
    
    
    @api.multi
    @api.constrains('phone')
    def _check_phone(self):
        for rec in self:
            if rec.phone and len(rec.phone) != 10:
                raise ValidationError(_("Invalid Phone Number..."))
        return True  

    def action_draft(self):
        self.state='draft'
       
       
    def action_out_service(self):
        self.state='out_service'
   
        
    def action_in_service(self):        
        if self.message_main_attachment_id.id is False:
            raise Warning(_("الرجاء ارفاق 12 س للمركبة"))   
        else:
            self.state='in_service'

    def get_maintenance_count(self):
        count = self.env['workshope.maintenance'].search_count([('chassis_id', '=', self.ids)])
        self.maintenance_count = count

    @api.multi
    def open_car_maintenance(self):
        return {
            'name': _('Maintenance'),
            'domain': [('chassis_id', '=', self.ids)],
            'view_type': 'form',
            'res_model': 'workshope.maintenance',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

class RsfWeaponLine(models.Model):
    _name = 'rsf.weapon.line'
    _description = ''
    _rec_name = ''

    weapon_name = fields.Many2one("rsf.weapon", string="Weapon Name")
    weapon_no = fields.Char('Weapon No', related="weapon_name.weapon_no")
    w_type = fields.Char("Type", related="weapon_name.weapon_type")
    the_number = fields.Char("The number")
    notes = fields.Text("Internal Note")
    car_id = fields.Many2one("workshope.cars")
