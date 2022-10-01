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


class SalesLinesIntegration(models.Model):
    _name = "sales.order.lines.integration"
    _description = "Sales Order Lines from Hotelia"

    name = fields.Char(String="Name", tracking=True)
    product_name = fields.Char(String="Description")
    price = fields.Integer(String="Price")
    order_id = fields.Many2one("sales.order.integration", String="Sales Order", required=True, ondelete='cascade', index=True, copy=False)
    product_uom_qty = fields.Integer(String="Quantity")





