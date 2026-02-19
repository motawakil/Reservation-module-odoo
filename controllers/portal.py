# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class ReservationPortal(CustomerPortal):

    # ------------------------------------------------------------------
    # Compteur sur /my
    # ------------------------------------------------------------------
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'reservation_count' in counters:
            values['reservation_count'] = (
                request.env['reservation.reservation']
                .search_count(self._get_reservations_domain())
            )
        return values

    def _get_reservations_domain(self):
        return [('partner_id', '=', request.env.user.partner_id.id)]

    # ------------------------------------------------------------------
    # /my/reservations
    # ------------------------------------------------------------------
    @http.route(
        ['/my/reservations', '/my/reservations/page/<int:page>'],
        type='http',
        auth='user',
        website=True,
    )
    def portal_my_reservations(self, page=1, sortby='date', filterby='all', **kw):

        domain = self._get_reservations_domain()

        searchbar_sortings = {
            'date':  {'label': _('Date'),      'order': 'reservation_start_date desc'},
            'name':  {'label': _('Reference'), 'order': 'name'},
            'state': {'label': _('Status'),    'order': 'state'},
        }
        sort_order = searchbar_sortings.get(sortby, searchbar_sortings['date'])['order']

        searchbar_filters = {
            'all':       {'label': _('All'),       'domain': []},
            'draft':     {'label': _('Draft'),     'domain': [('state', '=', 'draft')]},
            'confirmed': {'label': _('Confirmed'), 'domain': [('state', '=', 'confirmed')]},
            'cancelled': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancelled')]},
        }
        domain += searchbar_filters.get(filterby, searchbar_filters['all'])['domain']

        total = request.env['reservation.reservation'].search_count(domain)
        pager = portal_pager(
            url='/my/reservations',
            url_args={'sortby': sortby, 'filterby': filterby},
            total=total,
            page=page,
            step=10,
        )

        reservations = request.env['reservation.reservation'].search(
            domain,
            order=sort_order,
            limit=10,
            offset=pager['offset'],
        )

        values = {
            'reservations':       reservations,
            'page_name':          'reservation',
            'pager':              pager,
            'default_url':        '/my/reservations',
            'searchbar_sortings': searchbar_sortings,
            'sortby':             sortby,
            'searchbar_filters':  searchbar_filters,
            'filterby':           filterby,
        }

        
        return request.render(
            'reservation.portal_my_reservations',
            values,
        )

    # ------------------------------------------------------------------
    # /my/reservations/<id>
    # ------------------------------------------------------------------
    @http.route(
        '/my/reservations/<int:reservation_id>',
        type='http',
        auth='user',
        website=True,
    )
    def portal_reservation_detail(self, reservation_id, **kw):
        reservation = self._get_reservation_or_redirect(reservation_id)
        if not reservation:
            return request.redirect('/my/reservations')

        return request.render(
            'reservation.portal_reservation_detail',
            {'reservation': reservation, 'page_name': 'reservation'},
        )

    # ------------------------------------------------------------------
    # /my/reservations/<id>/pdf
    # ------------------------------------------------------------------
    @http.route(
        '/my/reservations/<int:reservation_id>/pdf',
        type='http',
        auth='user',
        website=True,
    )
    def portal_reservation_pdf(self, reservation_id, **kw):
        reservation = self._get_reservation_or_redirect(reservation_id)
        if not reservation:
            return request.redirect('/my/reservations')

        pdf_content, _ = (
            request.env['ir.actions.report']
            .sudo()
            ._render_qweb_pdf(
                'reservation.action_report_reservation',
                [reservation.id],
            )
        )
        filename = '%s.pdf' % reservation.name.replace('/', '_')
        return request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'attachment; filename="%s"' % filename),
            ],
        )

    # ------------------------------------------------------------------
    # Helper sécurité
    # ------------------------------------------------------------------
    def _get_reservation_or_redirect(self, reservation_id):
        reservation = (
            request.env['reservation.reservation']
            .sudo()
            .browse(reservation_id)
        )
        if not reservation.exists():
            return None
        if reservation.partner_id != request.env.user.partner_id:
            return None
        return reservation