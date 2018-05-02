# -*- coding: utf-8 -*-
import xlsxwriter
import base64
import sys
from openerp import api, fields, models, _
import datetime
from calendar import monthrange

class InvoiceReportService(models.TransientModel): 
	_name = 'account.invoice.report.service'

	@api.multi
	def _calculate_year(self):
		year = datetime.date.today().strftime("%Y")
		return [(str(int(year)-5), str(int(year)-5)),
				(str(int(year)-4), str(int(year)-4)),
				(str(int(year)-3), str(int(year)-3)),
				(str(int(year)-2), str(int(year)-2)),
				(str(int(year)-1), str(int(year)-1)),
				(str(int(year)), str(int(year))),
				(str(int(year) +1), str(int(year)+1)),
				(str(int(year)+2), str(int(year)+2)),
				(str(int(year)+3), str(int(year)+3)),
				(str(int(year)+4), str(int(year)+4)),
				(str(int(year)+5), str(int(year)+5)),]

	from_date = fields.Date(string="From Date")
	to_date = fields.Date(string="To Date")
	month = fields.Selection([('01','01'),
								('02','02'),
								('03','03'),
								('04','04'),
								('05','05'),
								('06','06'),
								('07','07'),
								('08','08'),
								('09','09'),
								('10','10'),
								('11','11'),
								('12','12')],string="Month")
	year = fields.Selection(_calculate_year,string="Year",default=datetime.date.today().strftime("%Y"))


	@api.multi
	def generate_report(self):
		invoice_ids = self.env[('account.invoice')].search([])
		if self.month:
			start_date = '01/'+ str(self.month) +"/" + str(self.year)
			start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
			month_day = monthrange(int(self.year),int(self.month))
			end_date = start_date + datetime.timedelta(days=int(month_day[1]))
			invoice_ids = self.env[('account.invoice')].search([('date_invoice','>=',start_date),('date_invoice','<=',end_date)])
		return {
				'name': _('Invoice Report'),
				'view_type': 'form',
				'view_mode': 'tree',
				'res_model': 'account.invoice',
				'view_id': self.env.ref('account_dgii.account_invoice_tree_report').id,
				'type': 'ir.actions.act_window',
				'domain':[('type','in',['in_invoice','in_refund']),('state','not in',['draft','cancel']),('id','in',invoice_ids and invoice_ids.ids or [])],
				'target': 'current',
				'context':{'category':True,'period':str(self.year)+str(self.month)}
			}

	@api.multi
	def print_report(self):
		context = dict(self._context or {})
		tmp_name = ''
		f_name = ''
		tmp_name='/tmp/invoice_report.xlsx'
		f_name = 'invoice_report.xlsx'

		workbook = xlsxwriter.Workbook(tmp_name)
		worksheet = workbook.add_worksheet()
		row = 0
		col = 0
		url_format = workbook.add_format({'bold':1})
		total_time_xl = []
		#1
		worksheet.write(row, col, 'Lineas', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		#2
		worksheet.write(row, col, 'Tax ID for Suppliers', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		#3
		worksheet.write(row, col, 'Tipo Id', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		#4
		worksheet.write(row, col, 'Tipo Bienes y Servicios Comprados', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		#5
		worksheet.write(row, col, 'NCF', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		#6
		worksheet.write(row, col, 'NCF Documento Modificado', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		#7
		worksheet.merge_range('G1:H1', 'Fecha Comprobante', url_format)
		worksheet.set_column(row, col, 20)
		col += 2
		#8
		worksheet.merge_range('I1:J1', 'Fecha Pago', url_format)
		worksheet.set_column(row, col, 20)
		col += 2
		#9
		worksheet.write(row, col, 'Itbis Facturado', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		#10
		worksheet.write(row, col, 'Itbis Retenido', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		#11
		worksheet.write(row, col, 'Monto Facturado', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		#12
		worksheet.write(row, col, 'Retencion Renta', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		row += 1
		lines = 1
		for rowdata in self.env['account.invoice'].browse(self._context.get('active_ids')):
			col = 0
			worksheet.set_column(row, col, 10)
			worksheet.write(row, col,lines)
			col += 1
			tax = rowdata.supplier_tax_no if rowdata.supplier_tax_no != 0 else ''
			worksheet.write(row, col,tax)
			col += 1

			worksheet.write(row, col,rowdata.tipo_id)
			col += 1

			worksheet.write(row, col,rowdata.type_good_services_id.code)
			col += 1

			worksheet.write(row, col,rowdata.ncf_no)
			col += 1

			worksheet.write(row, col,rowdata.ncf_doc_modification)
			col += 1

			worksheet.write(row, col,rowdata.receipt_year)
			col += 1

			worksheet.write(row, col,rowdata.receipt_date)
			col += 1

			worksheet.write(row, col,rowdata.pay_year)
			col += 1

			worksheet.write(row, col,rowdata.pay_date)
			col += 1

			billed_tax = "%.2f" % rowdata.billed_tax
			worksheet.write(row, col,billed_tax)
			col += 1

			withheld_tax = "%.2f" % rowdata.withheld_tax
			worksheet.write(row, col,withheld_tax)
			col += 1

			amount_untaxed = "%.2f" % rowdata.amount_untaxed
			worksheet.write(row, col,amount_untaxed)
			col += 1

			retention_tax = "%.2f" % rowdata.retention_tax
			worksheet.write(row, col,retention_tax)
			col += 1
			row += 1
			lines +=1

		workbook.close()

		with open(tmp_name, 'r') as myfile:
			data = myfile.read()
			myfile.close()
		result = base64.b64encode(data)

		attachment_obj = self.env['ir.attachment']
		attachment_id = attachment_obj.create({'name': f_name, 'datas_fname': f_name, 'datas': result})
		download_url = '/web/content/'+str(attachment_id.id)+'?download=true'#'model=ir.attachment&field=datas&filename_field=name&id=' + str(attachment_id.id)
		base_url = self.env['ir.config_parameter'].get_param('web.base.url')

		return {
			"type": "ir.actions.act_url",
			"url": str(base_url) + str(download_url),
			"target": "self",
		}

	@api.multi
	def print_text_report(self):
		name = '/home/ubuntu/txt/606.txt'  # Name of text file coerced with +.txt
		try:
			file = open(name,'w+')   # Trying to create a new file or open one
			untaxed_amount = 0.0
			rtn_tax = 0.0
			user_id = self.env['res.users'].search([('id','=',self._uid)])
			company_id = self.env['res.company'].search([('id','=',user_id.company_id.id)])
			period ='      '
			for rowdata in self.env['account.invoice'].browse(self._context.get('active_ids')):
				untaxed_amount += rowdata.amount_untaxed
				rtn_tax += rowdata.retention_tax
				period = rowdata.pay_year
			length = "%012d" % (len(self._context.get('active_ids')),) 
			rtn_tax = "%012.2f" % (abs(rtn_tax),) 
			untaxed_amount = "%016.2f" % (untaxed_amount,) 
			rnc_no = "{:>11}".format(str(company_id.rnc_no if company_id.rnc_no != 0 else ''))
			header_string = "606" + rnc_no + period + length + untaxed_amount + rtn_tax + "\n"

			file.write(header_string)
			length = len(self._context.get('active_ids'))
			for rowdata in self.env['account.invoice'].browse(self._context.get('active_ids')):
				supplier_tax_no = "{:<11}".format(str(rowdata.supplier_tax_no if rowdata.supplier_tax_no != 0 else ''))
				tipo_id = str(rowdata.tipo_id)
				type_good_services_id =  str(rowdata.type_good_services_id.code)
				ncf_no="{:<19}".format(str(rowdata.ncf_no))
				ncf_doc_modification ="{:<19}".format(str(rowdata.ncf_doc_modification if rowdata.ncf_doc_modification != 0 else ''))
				# ncf_doc_modification ="{:<19}".format(str(rowdata.ncf_doc_modification))
				receipt_year = str(rowdata.receipt_year)
				receipt_date = str(rowdata.receipt_date)
				pay_year = str(rowdata.pay_year)
				pay_date = str(rowdata.pay_date)
				billed_tax = "%012.2f" % (rowdata.billed_tax,)
				withheld_tax = "%012.2f" % (abs(rowdata.withheld_tax),)
				amount_untaxed = "%012.2f" % (rowdata.amount_untaxed,)  
				retention_tax = "%012.2f" % (abs(rowdata.retention_tax),) 
				string = supplier_tax_no + tipo_id +type_good_services_id+ ncf_no +  ncf_doc_modification + receipt_year + receipt_date + pay_year + pay_date + billed_tax + withheld_tax + amount_untaxed + retention_tax 
				if length> 1:
					string+="\n"
					length -=1

				file.write(string)
			file.close()

		except:
			print('Something went wrong! Can\'t tell what?')
			sys.exit(0) # quit Python
		with open(name, 'r') as myfile:
			data = myfile.read()
			myfile.close()
			result = base64.b64encode(data)
		attachment_obj = self.env['ir.attachment']
		attachment_id = attachment_obj.create({'name': name, 'datas_fname': name, 'datas': result})
		download_url = '/web/content/'+str(attachment_id.id)+'?download=true'#'model=ir.attachment&field=datas&filename_field=name&id=' + str(attachment_id.id)
		base_url = self.env['ir.config_parameter'].get_param('web.base.url')

		return {
			"type": "ir.actions.act_url",
			"url": str(base_url) + str(download_url),
			"target": "self",
		}

