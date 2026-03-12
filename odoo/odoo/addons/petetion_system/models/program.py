# -*- coding: utf-8 -*-

from odoo import models, fields


class Program(models.Model):
    _name = 'petetion.program'
    _description = 'Petition Program'

    name = fields.Char(
        string='Program Name',
        required=True,
        tracking=True
    )

    code = fields.Char(
        string='Program Code',
        required=True,
        tracking=True
    )

    description = fields.Text(
        string='Description'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Program Code must be unique!')
    ]
