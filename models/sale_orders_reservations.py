from odoo import models 

# In the same file or a new one
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_cancel(self):
        # 1. Run the standard SO cancel logic
        # super(): Odoo cancels the Sale Order, stops deliveries, and logs it in the chatter. then apply our logic 
        res = super(SaleOrder, self).action_cancel()
        
        # 2. Find linked reservations and cancel them too
        # We search for reservations where sale_order_id is this SO
        reservations = self.env['reservation.reservation'].search([
            ('sale_order_id', 'in', self.ids),
            ('state', '!=', 'cancelled')
        ])
        if reservations:
            reservations.write({'state': 'cancelled'})
            
        return res