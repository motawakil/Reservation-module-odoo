import base64
import io
import xlsxwriter
from odoo import models, fields, api

class ReservationExcelWizard(models.Model):
    _name = 'reservation.excel.wizard'
    _description = 'Wizard Export Excel'

    # Champs pour le filtrage par date
    date_start = fields.Date(string="Date Début", required=True)
    date_end = fields.Date(string="Date Fin", required=True)

    def action_export_excel(self):
        """ Génère le fichier Excel et déclenche le téléchargement """
        self.ensure_one()
        
        # 1. Récupérer les IDs sélectionnés depuis la vue liste (via le contexte)
        domain = [
            ('reservation_start_date', '<=', self.date_end),
            ('reservation_end_date', '>=', self.date_start),
        ]

        active_ids = self.env.context.get('active_ids')
        if active_ids:
            domain.append(('id', 'in', active_ids))

        reservations = self.env['reservation.reservation'].search(domain)


        # 3. Création du fichier Excel en mémoire (BytesIO)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet('Réservations')

        # Styles
        bold = workbook.add_format({'bold': True, 'bg_color': '#EEEEEE', 'border': 1})
        
        # En-têtes
        cols = ['Référence', 'Client', 'Date', 'Total']
        for i, col_name in enumerate(cols):
            sheet.write(0, i, col_name, bold)

        # Remplissage des lignes
        row = 1
        for res in reservations:
            sheet.write(row, 0, res.name)
            sheet.write(row, 1, res.partner_id.name)
            sheet.write(row, 2, str(res.reservation_date))
            sheet.write(row, 3, res.amount_total)
            row += 1

        workbook.close()
        output.seek(0)

        # 4. Encodage en base64 pour Odoo
        excel_file = base64.b64encode(output.read())
        
        # 5. Création d'un attachement temporaire pour le téléchargement
        attachment = self.env['ir.attachment'].create({
            'name': 'Rapport_Reservations.xlsx',
            'type': 'binary',
            'datas': excel_file,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        # 6. Retourne l'action de téléchargement URL
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }