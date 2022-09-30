import json
from datetime import date

import requests
from werkzeug.urls import url_encode
from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.tools import datetime
from odoo import _, http
from odoo.exceptions import UserError

class SOIntegration(models.Model):
    _name = "sales.order.integration"
    _description = "Sales Order from Hotelia"
    name = fields.Char(String="Name", tracking=True, translate=True)
    partner_name = fields.Char(String="Partner", tracking=True, translate=True)
    confirm_sale_status = fields.Boolean(String="Sales Order Generation")
    sales_lines = fields.One2many("sales.order.lines.integration", "order_id", string="Teams")


    @api.constrains('birth_date')
    def check_birth_date(self):
        current_date = datetime.now().date()
        for rec in self:
            if rec.birth_date > current_date:
                raise ValidationError("Birth date less than current date")

    @api.onchange('birth_date')
    def calculate_age(self):
        today = date.today()
        age = today.year - self.birth_date.year - (
                    (today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        if self.birth_date:
            self.age = age

    def confirm_sale(self):
        result = []
        for record in self:
            name = record.name + ' ' + record.partner_name
            result.append((record.id, name))
        return result

    def open_lead_team(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Teams',
            'view_mode': 'tree',
            'res_model': 'lead.team',
            'domain': [('lead_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def print_report_excel(self):
        return self.env.ref('crm_demo.lead_profile_card_xlsx').report_action(self)

    def action_shared_msteams(self):
        if not self.phone:
            raise ValidationError("The Lead has no Phone Number")
        message = 'Hi %s' % self.name
        # whatsapp_api_url = "https://api.whatsapp.com/send?phone=%s&text=%s" % (self.phone, message)
        ms_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        redirect_uri = "https://odoo.mitcloud.com/crm_demo/shared_ms_teams"
        params = dict(
            client_id='600068df-71d8-43ec-8252-4c373e418126',
            response_type='code',
            redirect_uri=redirect_uri,
            response_mode='query',
            scope='Chat.ReadBasic Chat.Read Chat.ReadWrite ChatMessage.Send',

            state=json.dumps({
                'email': self.email,
                'text': message,
                'id': self.id
            })
            # nonce=base64.urlsafe_b64encode(os.urandom(16)),
        )
        url = "%s?%s" % (ms_url, url_encode(params))

        # url = team_auth_endpt + 'client_id=' + client_id + '&response_type=code&redirect_uri=' + redirect_uri + '&response_mode=query&scope=offline_access%20chat.readbasic%20chat.read%20chat.readwrite%20chatmessage.send&state=12345'

        return {
            'type': 'ir.actions.act_url',
            'url': url
        }

    def action_shared_msteams_chat(self):
        data = {
            "body": {
                "content": "Hello " + self.name + ", Your Lead Data ID is " + str(self.id)
            }
        }

        body = json.dumps(data)

        chat_response = requests.post('https://graph.microsoft.com/v1.0/chats/' + self.chat_id + '/messages', data=body,
                                      headers={'Content-Type': 'application/json',
                                               'Authorization': 'Bearer %s' % self.access_token})

        if chat_response.status_code == 401:
            try:
                error_description = chat_response.json()['error_description']
            except Exception:
                error_description = _('Unknown error.')
            raise UserError(_('An error occurred when fetching the access token. %s') % error_description)

        chat_response_json = chat_response.json()
        self.chat_url = chat_response_json.get('webUrl')
        return "Your message is being shared to User"

    def compute_count(self):
        for record in self:
            record.team_count = self.env['lead.team'].search_count(
                [('lead_id', '=', self.id)])


class SalesLinesIntegration(models.Model):
    _name = "sales.order.lines.integration"
    _description = "Sales Order Lines from Hotelia"

    name = fields.Char(String="Name", tracking=True)
    product_name = fields.Char(String="Product Name")
    price = fields.Integer(String="Unit Price")
    order_id =fields.Many2one("sales.order.integration", String="Sales Order", ondelete="set null" )
    product_uom_qty = fields.Integer(String="Quantity")





