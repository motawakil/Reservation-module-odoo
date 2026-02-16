from odoo import models, fields, api


# this class is used to store (represent) every reservation line (product, quantity, price) linked to a reservation
# so one reservation can have multiple lines (products) and each line will have its own quantity and price
# that's why the reservation_id refers to one reservation (many2one) and the reservation line is linked to the reservation through the line_ids field (one2many) in the reservation model


class Reservation_line(models.Model):
    _name = 'reservation.line'
    _description = 'Reservation Line'


    reservation_id = fields.Many2one('reservation.reservation', string='Reservation', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    price_unit = fields.Float(
        string='Unit Price', 
        compute='_compute_price_unit', 
        readonly=False, 
        store=True, 
        precompute=True
    )
    subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)




    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price_unit

# this method is triggered when the product_id field changes, it updates the price_unit field with the list price of the selected product
    @api.depends('product_id')
    def _compute_price_unit(self):
        for rec in self:
            # Only set the price if product is set and price is 0 (to avoid overwriting manual edits)
            if rec.product_id:
                rec.price_unit = rec.product_id.list_price
            else:
                rec.price_unit = 0.0