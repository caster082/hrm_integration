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
    name = fields.Char(String="Bill No", tracking=True, translate=True)
    partner_name = fields.Char(String="Guest Name", tracking=True, translate=True)
    #partner_city = fields.Char(String="City", tracking=True, translate=True)
    #partner_country = fields.Integer(String="Country", tracking=True, translate=True)
    confirm_sale_status = fields.Boolean(String="Sales Order Generation")
    actual_sale_order_id = fields.Integer(String="Sales Order Id")
    bill_date = fields.Datetime(string="Bill Date")
    bill_amount = fields.Float(string="Bill Amount")
    price_list = fields.Many2one("product.pricelist", String="Payment Type", required=True, ondelete='cascade', index=True, copy=False)
    sales_lines = fields.One2many("sales.order.lines.integration", "order_id", string="Items", copy=True, auto_join=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Sales Order'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')





    def confirm_sale(self):
        partner = self.env['res.partner'].search([('name', '=', self.partner_name)])
        partner_id = 0
        product_id = 0
        if partner:
            partner_id = partner.id
        else:
            new_partner = self.env['res.partner'].create({
                'name': self.partner_name

            })
            partner_id = new_partner.id

        sale = self.env['sale.order'].create({
               'partner_id': partner_id

            })

        for sale_line in self.sales_lines:
            product = self.env['product.product'].search([('name', '=', sale_line.product_name)])
            if product:
                product_id = product.id
            else:
                new_product = self.env['product.product'].create({
                    'name': sale_line.name,

                })
                product_id = new_product.id
            sale_lines = self.env['sale.order.line'].create({

                'product_id': product_id,
                'price_unit': sale_line.price,
                'product_uom_qty': sale_line.product_uom_qty,
                'order_id': sale.id

            })
            #self.actual_sale_order_id = sale.id
            self.write({
           'actual_sale_order_id' : sale.id,
           'state': "done"
       })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale.id,
            'views': [(False, 'form')],
        }





    def change_draft(self):
        self.write({
            'state': "draft"
        })

    def open_sale_order(self):
        if self.actual_sale_order_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'res_id': self.actual_sale_order_id,
                'views': [(False, 'form')],
            }


    def connect_function(self):


        sale_inte_id = []
        sale_line={}
        index = 0
        stm_lines = None
        username = 'odooERP'
        password = 'fa02b9f9-4bae-45bb-8814-65195cf3962b'
        response = requests.get('http://159.223.177.229/api/v1/sales/sale.order', auth=(username, password), verify=False)
        response_line = requests.get('http://159.223.177.229/api/v1/sales/sale.order.line', auth=(username, password),
                                verify=False)
        response_partner = requests.get('http://159.223.177.229/api/v1/customer/res.partner', auth=(username, password),
                                     verify=False)


        response_json = response.json()
        response_line_json = response_line.json()
        response_partner_json = response_partner.json()
        # for val in response_line_json:
        #     sale_line[index] = {
        #         'id': val['id'],
        #         'name': val['name'],
        #         'product_id': val['product_id'],
        #         'price_unit': val['price_unit'],
        #         'order_id' : val['order_id'],
        #         'product_uom_qty': val['product_uom_qty']
        #     }
        #     index = index+1




        for val in response_json:

            existing_integration = self.env['sales.order.integration'].search([('name', '=', val['name'])])

            if existing_integration:
                continue

            partner_name = ''
            partner_city = ''
            partner_country = 0
            for partner in response_partner_json:
                if str(val['partner_id']) == str(partner['id']):
                    partner_name = partner['name']
                    #partner_city = partner ['city']
                    #partner_country = int(partner['country_id'])


            stm_lines = self.env['sales.order.integration'].create({

                'partner_name': partner_name,
                # 'price_unit': val['unit_price'],
                'name': val['name'],
                'price_list': val['pricelist_id'],
                'bill_date': val['date_order'],
                'bill_amount': val['amount_total'] + val['amount_tax']
                #'partner_city' : partner_city,
                #'partner_country' : partner_country
            })


            for order_line in val['order_line']:
                for val_line in response_line_json:
                    if str(val_line['id']) == str(order_line):
                        stm_lines1 = self.env['sales.order.lines.integration'].create({

                            'product_name': val_line['name'],
                            'name': val_line['name'],
                            # 'price_unit': val['unit_price'],
                            'product_uom_qty': val_line['product_uom_qty'],
                            'price': val_line['price_unit'],
                            'order_id': stm_lines.id,
                            'trans_date': val['date_order'],
                            'price_list': val['pricelist_id']

                        })

            sale_inte_id.append(stm_lines.id)

        return {
            'name': _('Generated Documents'),
            'res_model': 'sales.order.integration',
            'type': 'ir.actions.act_window',
            'context': "{'create': False}",
            'views': [[False, "tree"], [False, "kanban"], [False, "form"]],
            'view_mode': 'tree, kanban, form',
        }


class SalesLinesIntegration(models.Model):
    _name = "sales.order.lines.integration"
    _description = "Sales Order Lines from Hotelia"

    name = fields.Char(String="Name", tracking=True)
    product_name = fields.Char(String="Description")
    price = fields.Float(String="Price")
    trans_date = fields.Datetime(String="Transaction Date")
    price_list = fields.Many2one("product.pricelist", String="Customer Payment", required=True, ondelete='cascade',
                                 index=True, copy=False)
    order_id = fields.Many2one("sales.order.integration", String="Sales Order", required=True, ondelete='cascade', index=True, copy=False)
    product_uom_qty = fields.Integer(String="Quantity")





