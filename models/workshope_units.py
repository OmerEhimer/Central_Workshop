from odoo import api, fields, models
from odoo.tools.translate import _


class Workshopeunits(models.Model):
    _name = 'workshope.units'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Department'

    units_seq = fields.Char(string='units Seq', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'))

    name = fields.Char(string='Name',required=True,track_visibility="always")
    user_id = fields.Many2one('res.users',string="Resposible",readonly="1",default=lambda self:self.env.user)    

    _sql_constraints = [
        (
            'constraint_uniq_name',
            'unique(name)',
            'This Name Is Existed'
        ),
    ]  

    #this function for create sequence
    @api.model
    def create(self, vals):
        if vals.get('units_seq', _('New')) == _('New'):
           vals['units_seq'] = self.env['ir.sequence'].next_by_code('workshope.units.sequence') or _('New')
        result = super(Workshopeunits, self).create(vals)
        return result