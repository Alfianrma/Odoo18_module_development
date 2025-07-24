from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'

    name = fields.Char(required=True)
    property_ids = fields.One2many(
        comodel_name='estate.property',
        inverse_name='property_type_id',
        string='Properties'
    )
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'The property type name must be unique.')
    ]