from odoo import models, fields, api,Command
from odoo.exceptions import ValidationError


class Reservation(models.Model):

    # Fields Defintion 

    _name = 'reservation.reservation'
    _description = 'Reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # tracking=True enables the audit log in the chatter
    name = fields.Char(string='Reference', required=True, readonly=True, tracking=True, default='New', copy =False)
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
    






    # Action Methods for (confirm, cancel, view sale order)

    def action_confirm(self):
            for record in self: 
                # checks for at least one line of a reservation exist before confiramtion !!
                if not record.line_ids:
                    raise ValidationError('You cannot confirm a reservation without any lines.')
                
                # Create sales record (SO) if it doesn't exist
                if not record.sale_order_id:
                    record._create_new_sale_order()
                
                so = record.sale_order_id
                if so:
                    # If it was cancelled, move it back to Draft
                    if so.state == 'cancel':
                        so.action_draft() # method de sale.order to reset to draft
            return self.write({'state': 'confirmed'})

    def action_cancel(self): # cancel action
            for record in self:
                # If there is a linked Sale Order, cancel it too (if not already canceled/done)
                if record.sale_order_id and record.sale_order_id.state not in ['cancel', 'done']:
                    record.sale_order_id.action_cancel()
            
            return self.write({'state': 'cancelled'}) 



    def action_view_sale_order(self):
        self.ensure_one()
        # Prevent error if sale_order_id is empty ,
        if not self.sale_order_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Sale Order',
                    'message': 'There is no Sale Order linked to this reservation.',
                    'sticky': False,
                }
            }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_print_reservation(self):
        return self.env.ref('reservation.action_report_reservation').report_action(self)

# ----------------------------------------------------------------------------------------------------------------------------





    # method to create a sale order from the reservation lines, 
    # it is called when (confirming) -action_confirm- the reservation and there is no existing sale order linked to it


    def _create_new_sale_order(self):
            # Private helper to generate the Sale Order 
            self.ensure_one()
            sale_order = self.env['sale.order'].create({
                'partner_id': self.partner_id.id,
                'origin': self.name,  # Good practice to track origin
                'order_line': [Command.create({ # command to create one2many lines in the same transaction as the sale order creation  
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.price_unit,
                    'name': line.product_id.display_name, # Standard SO lines need a description
                }) for line in self.line_ids],
            })
            self.sale_order_id = sale_order.id
            return sale_order






# ----------------------------------------------------------------------------------------------------------------------------


    # Constraint to prevent confirming a reservation without any lines
    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('subtotal'))

   # Override the create method to assign a sequence number to the name field when a new reservation is created.
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New': # for every new record (Reservation) if the default = New . 
                # get the last sequence number for the model (reservation.reservation) and assign it to the name field, if there is no sequence defined it will return 'New' as default
                vals['name'] = self.env['ir.sequence'].next_by_code('reservation.reservation') or 'New'
        return super(Reservation, self).create(vals_list)
    

