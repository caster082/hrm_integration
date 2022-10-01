# -*- coding: utf-8 -*-
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class connect(models.Model):
    _name = "api_connect"
    _description = "HMS Connect API"

    name = fields.Char(string='API Name', required=True)
    method = fields.Char(string='Method', required=True)

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




        if sale_inte_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Connected',
                'view_mode': 'tree',
                'res_model': 'sales.order.integration',
                'context': "{'create': False}"
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Connected',
                'view_mode': 'tree',
                'res_model': 'sales.order.integration',
                'context': "{'create': False}"
            }

