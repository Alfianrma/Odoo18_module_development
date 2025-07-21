from odoo import models, fields,api
from dateutil.relativedelta import relativedelta

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'

    price  = fields.Float()
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        copy=False
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        index=True,
        copy=False
    )
    property_id = fields.Many2one(
        comodel_name='estate.property',
        string='Property',
        required=True,
        index=True,
        copy=False
    )
    validity = fields.Integer(
        string='Offer Validity (days)',
        default=7,
    )
    date_deadline = fields.Date(
        compute='_compute_date_deadline',
        string='Offer Deadline',
        store=True,
    )

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date and offer.validity:
                offer.date_deadline = offer.create_date + relativedelta(days=offer.validity)
            else:
                offer.date_deadline = fields.Date.today() + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.date_deadline and offer.validity:
                delta = offer.date_deadline - fields.Date.today()
                offer.validity = delta.days
            else:
                offer.validity = offer.date_deadline - fields.Date.today().days