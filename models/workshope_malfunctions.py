from odoo import api, fields, models
from odoo.tools.translate import _


class WorkshopeMalfunctions(models.Model):
    _name = 'workshoe.malfunctions'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Convert malfunctions'

    malfunctions_seq = fields.Char(string='Malfunctions Seq', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'))

    name = fields.Char(string='Name',required=True,track_visibility="always")
    malfunctions_type_id=fields.Many2one('workshope.malfunctions.type',string="Malfunctions Type",required=True,track_visibility="always" )   
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
        if vals.get('malfunctions_seq', _('New')) == _('New'):
           vals['malfunctions_seq'] = self.env['ir.sequence'].next_by_code('workshope.malfunctions.sequence') or _('New')
        result = super(WorkshopeMalfunctions, self).create(vals)
        return result