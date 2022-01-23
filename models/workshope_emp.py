from odoo import api, fields, models
from odoo.tools.translate import _


class WorkshopeEmployee(models.Model):
    _name = 'workshope.employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Department'
    _rec_name = 'engineer_name'

    emp_seq = fields.Char(string='Engineer Seq', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'))

    engineer_name = fields.Char(string='Engineer Name',required=True,track_visibility="always",) 
    card_number = fields.Char(string='Card NO', required=True,track_visibility="always")
    phone = fields.Char(string='Phone', required=True,track_visibility="always")
    location = fields.Char(string='Location', required=True,track_visibility="always")
    image = fields.Binary("Image")
    catt = fields.Selection([
        ('1', 'ضابط'),
        ('2', 'ضابط صف/جندي'),

    ], string="Category" , track_visibility="always",required=True, )    
    officcer = fields.Selection([
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
    
    warrant_officcer = fields.Selection([
        ('1', 'مساعد'),
        ('2', 'ر.أول'),
        ('3', 'رقيب'),
        ('4', 'عريف'),
        ('5', 'و.عريف'),
        ('6', 'جندي'),
        ('7', 'متعاقد'),
    ], string="Warrant Officer" , track_visibility="always",)
    section_ids = fields.Many2one('workshope.section', string="Department" ,required=True)
    # units_id = fields.Many2one('workshope.units',string="Units", required=True ,track_visibility="always")
    active = fields.Boolean(string="Active", default="True")
    maintenance_count = fields.Integer(compute="get_maintenance_count")
    internal_note = fields.Text("Internal Notes")
    #this function for create sequence
    @api.model
    def create(self, vals):
        if vals.get('emp_seq', _('New')) == _('New'):
           vals['emp_seq'] = self.env['ir.sequence'].next_by_code('workshope.employee.sequence') or _('New')
        result = super(WorkshopeEmployee, self).create(vals)
        return result

    def get_maintenance_count(self):
        count = self.env['workshope.maintenance'].search_count([('state','=','repaired'),('emp_line.emp_id', '=', self.id)])
        self.maintenance_count = count

    @api.multi
    def open_car_maintenance(self):
        return{
            'name':_('Maintenance times '),
            'domain':[('state','=','repaired'),('emp_line.emp_id','=', self.id)],
            'view_type':'form',
            'res_model':'workshope.maintenance',
            'view_id':False,
            'view_mode':'tree,form',
            'type':'ir.actions.act_window',
        }     


