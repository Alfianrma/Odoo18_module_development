from odoo import models,fields,api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = "Estate Property"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False,default=lambda self: fields.Datetime.now() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True,copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection = [
            ('north','North'),
            ('south','South'),
            ('east','East'),
            ('west','West')
        ]
    )
    active = fields.Boolean(default=False)
    state = fields.Selection(
        selection = [
            ('new','New'),
            ('offer_received','Offer Received'),
            ('offer_accepted','Offer Accepted'),
            ('sold','Sold'),
            ('canceled','Canceled')
        ],
        required=True,
        copy=False,
        default='new'
    )
    property_type_id = fields.Many2one(
        comodel_name='estate.property.type',
        string='Property Type',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Salesman',
        default=lambda self: self.env.user,
        index=True,
        # tracking=True
    )
    buyer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Buyer',
        copy=False,
        index=True,
        # tracking=True
    )
    tag_ids = fields.Many2many(
        comodel_name='estate.property.tag',
        string='Property Tags',
    )
    offer_ids = fields.One2many(
        comodel_name='estate.property.offer',
        inverse_name='property_id',
        string='Offers',
    )
    total_area = fields.Float(
        compute = '_compute_total_area',
        string='Total Area (sqm)',
    )
    best_price = fields.Float(
        compute='_compute_best_price',
        string='Best Offer',
    )

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.living_area + property.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for property in self:
            if property.offer_ids:
                property.best_price = max(property.offer_ids.mapped('price'))
            else:
                property.best_price = 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for property in self:
            if property.state == "canceled":
                raise UserError("You cannot mark a canceled property as sold.")
            else:
                property.state = 'sold'
                # property.selling_price = property.best_price
        return True

    def action_cancel(self):
        for property in self:
            if property.state == "sold":
                raise UserError("You cannot cancel a sold property.")
            else:
                property.state = 'canceled'
                # property.buyer_id = False
                # property.selling_price = 0.0
        return True

