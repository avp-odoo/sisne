# -*- coding: utf-8 -*-
import ast
from openerp import api, fields, models, _
import datetime


class GoodService(models.Model):
	_name = 'purchased.good.service'
	_rec_name = 'code'

	code = fields.Char(string='Code')
	name = fields.Char(string="Name")

	@api.multi
	def name_get(self):
		res = []
		if self._context.get('category'):
			return super(GoodService, self).name_get()
		else:
			for service in self:
				name = service.code +' - '+service.name
				res.append((service.id, name))
			return res


class AccountInvoice(models.Model):
	_inherit = "account.invoice"

	@api.multi
	def _get_tipoId(self):
		for invoice in self:
			partner_type = invoice.partner_id.company_type
			if partner_type == 'company':
				invoice.tipo_id = 1
			else:
				invoice.tipo_id = 2

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
	def _get_receipt_year(self):
		for invoice in self:
			invoice.receipt_year= invoice.date_invoice and datetime.datetime.strptime(invoice.date_invoice,'%Y-%m-%d').strftime('%Y%m')
			invoice.receipt_date = invoice.date_invoice and  datetime.datetime.strptime(invoice.date_invoice,'%Y-%m-%d').strftime('%d')
		
	@api.multi
	def _get_tax_calculation(self):
		billed_tax = 0.0
		withheld_tax = 0.0
		retention_tax = 0.0
		for invoice in self:
			category = {}
			for tax in invoice.tax_line_ids:
				amount = 0.0
				if tax.tax_id.category_id:
					if not category.has_key(tax.tax_id.category_id.name):
						category.update({tax.tax_id.category_id.name:tax.amount})
					else:
						amount = category.get(tax.tax_id.category_id.name)
						category.update({tax.tax_id.category_id.name:amount + tax.amount})
			invoice.billed_tax = category and category.get('Itbis Facturado') or 0.0
			invoice.withheld_tax = category and category.get('Itbis Retenido') or 0.0
			invoice.retention_tax = category and category.get('Retencion Renta') or 0.0

	@api.multi
	def _get_tax_no(self):
		for invoice in self:
			if invoice.partner_id.company_type =='person': 
				invoice.supplier_tax_no = invoice.partner_id.cedula
			else:
				invoice.supplier_tax_no = invoice.partner_id.rnc

	ncf_no = fields.Char(string='NCF No',size=19)
	supplier_tax_no = fields.Char(compute="_get_tax_no",string="Tax ID for Suppliers")
	type_good_services_id = fields.Many2one('purchased.good.service',string="Tipo Bienes y Servicios Comprados")
	ncf_doc_modification = fields.Char(string='NCF o Documento Modificado',size=19)
	tipo_id = fields.Char(compute="_get_tipoId", string="Tipo Id")
	receipt_year = fields.Char(compute="_get_receipt_year", string="Invoice Year")
	receipt_date = fields.Char(compute="_get_receipt_year", string="Invoice Date")
	pay_year = fields.Char(compute="_get_pay_year",string="Pay Year")
	pay_date = fields.Char(compute="_get_pay_year", string="Pay Date")
	billed_tax = fields.Float(compute="_get_tax_calculation", string="Itbis Facturado")
	withheld_tax = fields.Float(compute="_get_tax_calculation", string="Itbis Retenido")
	retention_tax = fields.Float(compute="_get_tax_calculation", string="Retencion Renta")

class AccountTax(models.Model):
	_inherit = 'account.tax'

	include_606 = fields.Boolean(string='Include in 606')
	category_id = fields.Many2one('account.tax.category', string="606 (Category)")
	
class AccountTaxCategory(models.Model):
	_name = 'account.tax.category'

	name = fields.Char(string='Name')


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
			    	next_inv_id.ncf_doc_modification = invoice_id.ncf_no
    	return res
