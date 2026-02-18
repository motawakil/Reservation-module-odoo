from odoo import models, fields, tools


class ReservationReport(models.Model):
    _name = 'reservation.report'
    _description = 'Reservation Analysis'
    _auto = False
    _rec_name = 'partner_id'
    _order = 'partner_id'

    partner_id = fields.Many2one('res.partner',string='Customer', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', readonly=True)

    total_paid = fields.Float(
        string='Total Paid',
        readonly=True,
        aggregator='sum'
    )
    reservation_count = fields.Integer(
        string='Reservations',
        readonly=True,
        aggregator='sum'
    )
    line_count = fields.Integer(
        string='Lines',
        readonly=True,
        aggregator='sum'
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE VIEW reservation_report AS (
                SELECT
                    row_number() OVER ()         AS id,
                    r.partner_id                 AS partner_id,
                    r.state                      AS state,
                    SUM(r.amount_total)          AS total_paid,
                    COUNT(DISTINCT r.id)         AS reservation_count,
                    COUNT(l.id)                  AS line_count
                FROM reservation_reservation r
                LEFT JOIN reservation_line l
                    ON l.reservation_id = r.id
                GROUP BY r.partner_id, r.state
            )
        """)