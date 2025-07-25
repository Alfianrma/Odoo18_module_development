from odoo import models, fields,api
from odoo.exceptions import UserError,ValidationError
from odoo.tools.float_utils import float_is_zero,float_compare
from dateutil.relativedelta import relativedelta

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

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

    def action_accept(self):
        for offer in self:
            if offer.property_id.state == 'sold':
                raise UserError("Cannot accept an offer for a property that is already sold.")
            else:
                offer.status = 'accepted'
                offer.property_id.state = 'sold'
                offer.property_id.selling_price = offer.price
                offer.property_id.buyer_id = offer.partner_id
        return True

    def action_refuse(self):
        for offer in self:
            if offer.property_id.state == 'sold':
                raise UserError("Cannot refuse an offer for a property that is already sold.")
            else:
                offer.status = 'refused'
        return True
    
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The offer price must be positive.'),
        ('check_validity', 'CHECK(validity > 0)', 'The offer validity must be positive.'),
    ]

    @api.constrains('price', 'property_id')
    def _check_price_property(self):
        for offer in self:
            if float_compare(offer.price, offer.property_id.expected_price * 0.9, precision_digits=2) < 0:
                raise ValidationError("Selling price cannot be less than 90% of expected price.")