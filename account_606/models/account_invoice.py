# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    ncf = fields.Char(string='NCF No')
    ncf_modification = fields.Char(string='NCF o Documento Modificado', size=19)
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
    tipo_id = fields.Char(compute="_get_tipoId", string="Tipo Id")
    pay_year = fields.Char(compute="_get_pay_year",string="Pay Year")
    pay_date = fields.Char(compute="_get_pay_year", string="Pay Date")

    @api.multi
    def _get_pay_year(self):
        for invoice in self:
            invoice_pay_date = '' # taken a last date of payment
            for payment in invoice.payment_ids:
                invoice_pay_date = payment.payment_date
            if not invoice_pay_date:
                invoice_pay_date = invoice.date_invoice
            invoice.pay_year= invoice_pay_date and datetime.datetime.strptime(invoice_pay_date,'%Y-%m-%d').strftime('%Y%m')
            invoice.pay_date = invoice_pay_date and  datetime.datetime.strptime(invoice_pay_date,'%Y-%m-%d').strftime('%d')

    @api.multi
    def _get_tipoId(self):
        for invoice in self:
            partner_type = invoice.partner_id.company_type
            if partner_type == 'company':
                invoice.tipo_id = 1
            else:
                invoice.tipo_id = 2

    @api.constrains('ncf')
    def check_format_ncf(self):
        #check length
        for invoice in self:
            if invoice.ncf and invoice.type in ('in_invoice','in_refund'):
                if len(invoice.ncf) != 11 or invoice.ncf[0].isdigit() or invoice.ncf[0] != 'A' or (not invoice.ncf[1:].isdigit()):
                    raise ValidationError(_('The NCF number [%s] does not seem to be valid. \nNote: the expected format is A0123456789'))

    @api.model
    def set_ncf(self):
        module_dgii_installed = self.env['ir.module.module'].search([('name', '=', 'account_dgii'), ('state', '=', 'installed')])
        if module_dgii_installed:
            self._cr.execute('UPDATE account_invoice SET ncf=ncf_no, ncf_modification=ncf_doc_modification')

class AccountInvoiceRefund(models.TransientModel):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"
    _description = "Invoice Refund"


    @api.multi
    def invoice_refund(self):
        res = super(AccountInvoiceRefund, self).invoice_refund()
        if res.get('domain'):
            next_id = []
            for domain in res.get('domain'):
                if domain[0] == 'id':
                    next_id = domain[2]
                    inv_obj = self.env['account.invoice']
                    next_inv_id = inv_obj.browse(next_id)
                    invoice_id = inv_obj.browse(self._context.get('active_ids'))
                    next_inv_id.ncf_modification = invoice_id.ncf
        return res