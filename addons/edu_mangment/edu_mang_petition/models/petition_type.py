from odoo import models, fields, api

class PetitionType(models.Model):
    _name = 'petition.type'
    _description = 'Petition Type'
    _order = 'sequence, name'

    name = fields.Char(string='Petition Type', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    requires_approval = fields.Boolean(string='Requires Approval', default=True)
    max_duration_days = fields.Integer(string='Max Duration (Days)', help='Maximum days for this petition type')
    
    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Petition Type code must be unique!')
    ]