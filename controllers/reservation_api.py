# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError


class ReservationAPI(http.Controller):
    """
    JSON API Controller for Reservation module.
    This controller exposes REST endpoints for external usage (Postman, mobile app, portal).
    """

    # ============================================================
    # CREATE RESERVATION
    # Endpoint: POST /api/reservation/create
    # Auth: Logged-in user required
    # ============================================================

    @http.route(
        '/api/reservation/create',
        type='json',
        auth='user',
        methods=['POST'],
        csrf=False,       # Required for Postman / external API calls
        cors='*'          # Allow external JS requests (future portal/mobile)
    )
    def create_reservation(self, **kwargs):
        """
        Create a new reservation with lines.

        Expected JSON body:
        {
            "partner_id": 7,
            "reservation_start_date": "2026-02-20",
            "reservation_end_date": "2026-02-25",
            "lines": [
                {"product_id": 15, "quantity": 2},
                {"product_id": 18, "quantity": 1}
            ]
        }
        """

        try:
            user = request.env.user

            # ----------------------------------------------------
            # 1️⃣ Check group permission
            # ----------------------------------------------------
            if not user.has_group('reservation.reservation_group_users'):
                return {
                    "success": False,
                    "message": "Access denied. User not allowed to create reservations.",
                    "data": {}
                }

            # ----------------------------------------------------
            # 2️⃣ Get JSON data
            # ----------------------------------------------------
            data = request.jsonrequest or {}

            required_fields = [
                'partner_id',
                'reservation_start_date',
                'reservation_end_date',
                'lines'
            ]

            for field in required_fields:
                if field not in data:
                    return {
                        "success": False,
                        "message": f"Missing required field: {field}",
                        "data": {}
                    }

            if not isinstance(data.get('lines'), list) or not data['lines']:
                return {
                    "success": False,
                    "message": "Lines must be a non-empty list.",
                    "data": {}
                }

            # ----------------------------------------------------
            # 3️⃣ Prepare reservation values
            # ----------------------------------------------------
            reservation_vals = {
                "partner_id": data["partner_id"],
                "reservation_start_date": data["reservation_start_date"],
                "reservation_end_date": data["reservation_end_date"],
            }

            reservation = request.env['reservation.reservation'].sudo().create(reservation_vals)

            # ----------------------------------------------------
            # 4️⃣ Create reservation lines
            # ----------------------------------------------------
            for line in data["lines"]:
                if "product_id" not in line:
                    return {
                        "success": False,
                        "message": "Each line must contain product_id.",
                        "data": {}
                    }

                request.env['reservation.line'].sudo().create({
                    "reservation_id": reservation.id,
                    "product_id": line["product_id"],
                    "quantity": line.get("quantity", 1.0),
                })

            # ----------------------------------------------------
            # 5️⃣ Successful response
            # ----------------------------------------------------
            return {
                "success": True,
                "message": "Reservation created successfully.",
                "data": {
                    "id": reservation.id,
                    "name": reservation.name,
                    "state": reservation.state,
                    "partner_id": reservation.partner_id.id,
                    "start_date": reservation.reservation_start_date,
                    "end_date": reservation.reservation_end_date,
                    "amount_total": reservation.amount_total,
                }
            }

        # --------------------------------------------------------
        # Business validation errors
        # --------------------------------------------------------
        except ValidationError as e:
            return {
                "success": False,
                "message": str(e),
                "data": {}
            }

        # --------------------------------------------------------
        # Access errors
        # --------------------------------------------------------
        except AccessError:
            return {"success": False,  "message": "Access error.", "data": {}}

        # --------------------------------------------------------
        # Unexpected errors
        # --------------------------------------------------------
        except Exception as e:
            return {
                "success": False, 
                "message": "Internal server error.", 
                "data": {}
            }









    # ============================================================
    # GET /api/reservation/<id>
    # ============================================================

    @http.route(
        '/api/reservation/<int:res_id>',
        type='json',
        auth='user',
        methods=['GET'],
        csrf=False,
        cors='*'
    )
    def get_reservation(self, res_id):

        try:
            user = request.env.user

            if not user.has_group('reservation.reservation_group_users'):
                return {"success": False, "message": "Access denied.", "data": {}}

            reservation = request.env['reservation.reservation'].browse(res_id)

            if not reservation.exists():
                return {"success": False, "message": "Reservation not found.", "data": {}}

            lines_data = []
            for line in reservation.line_ids:
                lines_data.append({
                    "product_id": line.product_id.id,
                    "product_name": line.product_id.display_name,
                    "quantity": line.quantity,
                    "price_unit": line.price_unit,
                    "subtotal": line.subtotal,
                })

            return {
                "success": True,
                "message": "Reservation retrieved.",
                "data": {
                    "id": reservation.id,
                    "name": reservation.name,
                    "partner_id": reservation.partner_id.id,
                    "partner_name": reservation.partner_id.display_name,
                    "state": reservation.state,
                    "start_date": reservation.reservation_start_date,
                    "end_date": reservation.reservation_end_date,
                    "amount_total": reservation.amount_total,
                    "lines": lines_data,
                }
            }

        except Exception:
            return {"success": False, "message": "Internal server error.", "data": {}}








    # ============================================================
    # GET /api/reservations
    # ============================================================

    @http.route(
        '/api/reservations',
        type='json',
        auth='user',
        methods=['GET'],
        csrf=False,
        cors='*'
    )
    def list_reservations(self, **kwargs):

        try:
            user = request.env.user

            if not user.has_group('reservation.reservation_group_users'):
                return {"success": False, "message": "Access denied.", "data": {}}

            reservations = request.env['reservation.reservation'].search([])

            data = []
            for r in reservations:
                data.append({
                    "id": r.id,
                    "name": r.name,
                    "partner_name": r.partner_id.display_name,
                    "state": r.state,
                    "start_date": r.reservation_start_date,
                    "end_date": r.reservation_end_date,
                    "amount_total": r.amount_total,
                })

            return {
                "success": True,
                "message": "Reservations list.",
                "data": data
            }

        except Exception:
            return {"success": False, "message": "Internal server error.", "data": {}}










    # ============================================================
    # POST /api/reservation/<id>/confirm
    # ============================================================

    @http.route(
        '/api/reservation/<int:res_id>/confirm',
        type='json',
        auth='user',
        methods=['POST'],
        csrf=False,
        cors='*'
    )
    def confirm_reservation(self, res_id):

        try:
            user = request.env.user

            if not user.has_group('reservation.reservation_group_users'):
                return {"success": False, "message": "Access denied.", "data": {}}

            reservation = request.env['reservation.reservation'].browse(res_id)

            if not reservation.exists():
                return {"success": False, "message": "Reservation not found.", "data": {}}

            reservation.action_confirm()

            return {
                "success": True,
                "message": "Reservation confirmed.",
                "data": {
                    "id": reservation.id,
                    "state": reservation.state
                }
            }

        except Exception:
            return {"success": False, "message": "Internal server error.", "data": {}}










    # ============================================================
    # POST /api/reservation/<id>/cancel
    # ============================================================

    @http.route(
        '/api/reservation/<int:res_id>/cancel',
        type='json',
        auth='user',
        methods=['POST'],
        csrf=False,
        cors='*'
    )
    def cancel_reservation(self, res_id):

        try:
            user = request.env.user

            if not user.has_group('reservation.reservation_group_users'):
                return {"success": False, "message": "Access denied.", "data": {}}

            reservation = request.env['reservation.reservation'].browse(res_id)

            if not reservation.exists():
                return {"success": False, "message": "Reservation not found.", "data": {}}

            reservation.action_cancel()

            return {
                "success": True,
                "message": "Reservation cancelled.",
                "data": {
                    "id": reservation.id,
                    "state": reservation.state
                }
            }

        except Exception:
            return {"success": False, "message": "Internal server error.", "data": {}}