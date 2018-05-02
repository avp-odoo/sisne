# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    tipo = fields.Selection([
            ('01','01-GASTOS DE PERSONAL'),
            ('02','02-GRASTOS POR TRABAJOS, SUMINISTROS Y SERVICIOS'),
            ('03','03-ARRENDAMIENTOS'),
            ('04','04-GASTOS DE ACTIVOS FIJO'),
            ('05','05-GASTOS DE REPRESENTACION'),
            ('06','06-OTRAS DEDUCCIONES ADMITIDAS'),
            ('07','07-GASTOS FINANCIEROS'),
            ('08','08-GASTOS EXTRAORDINARIOS'),
            ('09','09-COMPRAS Y GASTOS QUE FORMARAN PARTE DEL COSTO DE VENTA'),
            ('10','10-ADQUISICIONS DE ACTIVOS'),
            ('11','11-GASTOS DE SEGURO'),
        ], string='Tipo', help='Type of Purchase')

    @api.constrains('ncf_no')
    def check_format_ncf(self):
        #check length
        print "called"
        for invoice in self:
            if invoice.ncf_no and invoice.type in ('in_invoice','in_refund'):
                print "iNnnnnnnn"
                if len(invoice.ncf_no) != 11 or invoice.ncf_no[0].isdigit() or invoice.ncf_no[0] != 'A' or (not invoice.ncf_no[1:].isdigit()):
                    print "rrrrrrrrrrr"
                    raise ValidationError(_('The NCF number [%s] does not seem to be valid. \nNote: the expected format is A0123456789'))

