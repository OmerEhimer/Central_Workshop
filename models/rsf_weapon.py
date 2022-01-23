from odoo import api, fields, models
from odoo.tools.translate import _


class RsfWeapon(models.Model):
    _name = 'rsf.weapon'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'rsf weapon'
    _rec_name = 'name'

    @api.multi
    def name_get(self) :
        res = []
        for field in self :
            res.append((field.id, '%s - %s' % (field.weapon_seq, field.name)))
        return res

    weapon_seq = fields.Char(string='Weapon Seq', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'))

    image = fields.Binary("Image")
    name = fields.Char("Weapon Name", required=True, track_visibility='always')
    weapon_no = fields.Char('Weapon No', required=True, track_visibility='always')
    weapon_type = fields.Char('Weapon Type', required=True, track_visibility='always')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_service', 'In Service'),
        ('out_service', 'Out Service'),
        ('scrap', 'Scrap'),
    ], string="Weapon State", readonly=True, default='draft',)
    #this function for create sequence
    @api.model
    def create(self, vals):
        if vals.get('weapon_seq', _('New')) == _('New'):
           vals['weapon_seq'] = self.env['ir.sequence'].next_by_code('rsf.weapon.sequence') or _('New')
        result = super(RsfWeapon, self).create(vals)
        return result
    
    def in_service(self):
        self.state = 'in_service'

    def out_service(self):
        self.state = 'out_service'

    def scrap(self):
        self.state = 'scrap'