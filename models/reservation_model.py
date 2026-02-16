from odoo import models, fields, api

class Reservation(models.Model):
    _name = 'reservation.reservation'
    _description = 'Reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # tracking=True enables the audit log in the chatter
    name = fields.Char(string='Reference', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    reservation_date = fields.Datetime(string='Reservation Date', required=True, default=fields.Datetime.now)
    
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('confirmed', 'Confirmed'), 
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    line_ids = fields.One2many('reservation.line', 'reservation_id', string='Reservation Lines')
    sale_order_id = fields.Many2one('sale.order', string='Related Sale Order')
    amount_total = fields.Float(string='Total Amount', compute='_compute_amount_total', store=True)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('subtotal'))