from odoo import api, fields, models
from odoo.tools.translate import _


class WorkshopeMalfunctionsType(models.Model):
    _name = 'workshope.malfunctions.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Convert Service Type'

    malfunctions_type_seq = fields.Char(string='Malfunctions Type Seq', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'))

    name = fields.Char(string='Name',required=True,track_visibility="always")
    weight = fields.Integer('Weight' , required=True)
    user_id = fields.Many2one('res.users',string="Resposible", readonly="1", default=lambda self:self.env.user)
    
    # ------- sql query ------- #
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
        if vals.get('malfunctions_type_seq', _('New')) == _('New'):
           vals['malfunctions_type_seq'] = self.env['ir.sequence'].next_by_code('workshope.malfunctions.type.sequence') or _('New')
        result = super(WorkshopeMalfunctionsType, self).create(vals)
        return result