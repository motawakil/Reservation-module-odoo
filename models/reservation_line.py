from odoo import models, fields, api

class Reservation_line(models.Model):
    _name = 'reservation.line'
    _description = 'Reservation Line'


    reservation_id = fields.Many2one('reservation.reservation', string='Reservation', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True, default=0.0)
    subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)




    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price_unit
