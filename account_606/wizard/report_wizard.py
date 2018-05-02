# -*- coding: utf-8 -*-
import xlsxwriter
import base64
import sys
import re
from openerp import api, fields, models, _
import datetime
from calendar import monthrange


class InvoiceReportService(models.TransientModel): 
	_name = 'account.invoice.report.service.606'

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
	year = fields.Selection(_calculate_year, string="Year", default=datetime.date.today().strftime("%Y"))

	def vendor_bills(self):
		domain = [('type','in',['in_invoice','in_refund'])]
		invoice_ids = self.env[('account.invoice')].search(domain)
		if self.month:
			start_date = '01/'+ str(self.month) +"/" + str(self.year)
			start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
			month_day = monthrange(int(self.year),int(self.month))
			end_date = start_date + datetime.timedelta(days=int(month_day[1]))
			domain += ('date_invoice','>=',start_date),('date_invoice','<',end_date)
			print "domainnnn",domain
			invoice_ids = self.env[('account.invoice')].search(domain)
		if invoice_ids:
			invoice_ids = invoice_ids.filtered(lambda inv: inv.state not in ['draft','cancel'])
		return invoice_ids

	def _remove_ascii_char(self, text):
		return re.sub(r'[^\x00-\x7F]+',' ', text)

	@api.multi
	def print_report_custom(self):
		context = dict(self._context or {})
		tmp_name='/tmp/invoice_report.xlsx'
		file_name = '606'
		if self.year:
			file_name = file_name + str(self.year)

		if self.month:
			file_name = file_name + str(self.month)

		f_name = file_name + '.xlsx'

		workbook = xlsxwriter.Workbook(tmp_name)
		worksheet = workbook.add_worksheet()
		invoice_ids = self.vendor_bills()
		
		row = 0
		col = 0
		
		url_format = workbook.add_format({'bold':1})
		total_time_xl = []
		
		### Header Part ###
		worksheet.write(row, col, self._remove_ascii_char('Código Información'), url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		worksheet.write(row, col, self._remove_ascii_char('RNC o Cédula'), url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		worksheet.write(row, col, self._remove_ascii_char('Periodo'), url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		worksheet.write(row, col, self._remove_ascii_char('Cantidad Registros'), url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		row += 1

		col = 0
		worksheet.write(row, col, "606")
		worksheet.set_column(row, col, 20)
		col += 1
		
		# Company Detail
		rnc_no = ''
		if self.env.user and self.env.user.company_id:
			company = self.env.user.company_id
			if company.rnc_no and len(company.rnc_no) == 11:
				rnc_no = company.rnc_no

		worksheet.write(row, col, rnc_no)
		worksheet.set_column(row, col, 20)
		col += 1
		
		worksheet.write(row, col, str(self.year) + str(self.month))
		worksheet.set_column(row, col, 20)
		col += 1

		worksheet.write(row, col, str(len(invoice_ids)).zfill(12))
		worksheet.set_column(row, col, 20)
		col += 1
		row += 4

		#1 rnc
		col = 0
		worksheet.write(row, col, self._remove_ascii_char('RNC o Cédula'), url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#2
		worksheet.write(row, col, 'Tipo Id', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#3
		worksheet.write(row, col, self._remove_ascii_char('Tipo Bienes y Servicios Comprados'), url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#4
		worksheet.write(row, col, 'NCF', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#5
		worksheet.write(row, col, 'NCF Documento Modificado', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#6
		worksheet.write(row, col, 'Fecha Comprobante', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#7
		worksheet.write(row, col, 'Fecha Pago', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#8
		worksheet.write(row, col, 'Monto Facturado en Servicios', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#9
		worksheet.write(row, col, 'Monto Facturado en Bienes', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#10
		worksheet.write(row, col, 'Total Monto Facturado', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#11
		worksheet.write(row, col, 'ITBIS Facturado', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#12
		worksheet.write(row, col, 'Itbis Retenido', url_format)
		worksheet.set_column(row, col, 20)
		col += 1
		
		#13
		worksheet.write(row, col, 'ITBIS sujeto a Proporcionalidad (Art. 349)', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#14
		worksheet.write(row, col, 'ITBIS llevado al Costo', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#15
		worksheet.write(row, col, 'ITBIS por Adelantar', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#16
		worksheet.write(row, col, 'ITBIS percibido en compras', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#17
		worksheet.write(row, col, self._remove_ascii_char('Tipo de Retención en ISR'), url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#18
		worksheet.write(row, col, self._remove_ascii_char('Monto Retención Renta'), url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#19
		worksheet.write(row, col, 'ISR Percibido en compras', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#20
		worksheet.write(row, col, 'Impuesto Selectivo al Consumo', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#21
		worksheet.write(row, col, 'Otros Impuestos/Tasas', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#22
		worksheet.write(row, col, 'Monto Propina Legal', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		#23
		worksheet.write(row, col, 'Forma de Pago', url_format)
		worksheet.set_column(row, col, 20)
		col += 1

		row += 1
		lines = 1

		# for rowdata in self.env['account.invoice'].browse(self._context.get('active_ids')):
		for rowdata in invoice_ids:
			col = 0
			rnc = ''
			if rowdata.partner_id and rowdata.partner_id.is_company:
				rnc = rowdata.partner_id.rnc and rowdata.partner_id.rnc.zfill(9) or ''
			else:
				rnc = rowdata.partner_id.cedula and rowdata.partner_id.cedula.zfill(11) or ''

			#1
			worksheet.set_column(row, col, 10)
			worksheet.write(row, col, rnc)
			col += 1
			
			#2
			worksheet.write(row, col, rowdata.tipo_id)
			col += 1

			#3
			worksheet.write(row, col, rowdata.tipo)
			col += 1

			#4
			worksheet.write(row, col, rowdata.ncf_no)
			col += 1
			
			#5
			worksheet.write(row, col, rowdata.ncf_doc_modification)
			col += 1
			
			#6
			worksheet.write(row, col, datetime.datetime.strptime(rowdata.date_invoice, '%Y-%m-%d').strftime('%Y%m%d'))
			col += 1

			#7
			pay_date = ""
			if rowdata.pay_year and rowdata.pay_date:
				pay_date = rowdata.pay_year + rowdata.pay_date
			worksheet.write(row, col, pay_date) #datetime.datetime.strptime(rowdata.pay_date, '%Y-%m-%d').strftime('%Y%m')
			col += 1
			
			#8 Total of service type product without tax
			total_monto_facturado_en_servicios = sum([line.quantity * line.price_unit for line in rowdata.invoice_line_ids if line.product_id and line.product_id.type == 'service'])
			total_monto_facturado_en_servicios = ("%.2f" % (total_monto_facturado_en_servicios)).zfill(12)
			worksheet.write(row, col, total_monto_facturado_en_servicios)
			col += 1

			#9 Total of not service type product without tax
			total_monto_facturado_en_bienes = sum([line.quantity * line.price_unit for line in rowdata.invoice_line_ids if line.product_id and line.product_id.type != 'service'])
			total_monto_facturado_en_bienes = ("%.2f" % (total_monto_facturado_en_bienes)).zfill(12)
			worksheet.write(row, col, total_monto_facturado_en_bienes)
			col += 1

			#10 Total amount without tax
			amount_untaxed = ("%.2f" % (rowdata.amount_untaxed)).zfill(12)
			worksheet.write(row, col, amount_untaxed)
			col += 1

			# Tax Updates
			itbis_facturado_price = 0.00
			itbis_retenido_price = 0.00
			itbis_sujeto_troporcionalidad_price = 0.00
			itbis_llevado_price = 0.00
			monto_retencion_renta_price = 0.00
			impuesto_selectivo_al_consumo_price = 0.00
			otros_impuestos_price = 0.00
			monto_propina_legal_price = 0.00

			for line in rowdata.invoice_line_ids:
				taxes = line.mapped("invoice_line_tax_ids")
				itbis_facturado = taxes.filtered(lambda x: x.itbis_facturado)
				itbis_retenido = taxes.filtered(lambda x: x.itbis_retenido)
				itbis_sujeto_troporcionalidad = taxes.filtered(lambda x: x.itbis_sujeto_troporcionalidad)
				itbis_llevado = taxes.filtered(lambda x: x.itbis_llevado)
				monto_retencion_renta = taxes.filtered(lambda x: x.monto_retencion_renta)
				impuesto_selectivo_al_consumo = taxes.filtered(lambda x: x.impuesto_selectivo_al_consumo)
				otros_impuestos = taxes.filtered(lambda x: x.otros_impuestos)
				monto_propina_legal = taxes.filtered(lambda x: x.monto_propina_legal)

				price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
				
				itbis_facturado_tax_data = itbis_facturado.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
				itbis_retenido_tax_data = itbis_retenido.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
				itbis_sujeto_troporcionalidad_tax_data = itbis_sujeto_troporcionalidad.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
				itbis_llevado_tax_data = itbis_llevado.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
				monto_retencion_renta_tax_data = monto_retencion_renta.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
				impuesto_selectivo_al_consumo_tax_data = impuesto_selectivo_al_consumo.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
				otros_impuestos_tax_data = otros_impuestos.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
				monto_propina_legal_tax_data = monto_propina_legal.compute_all(price, rowdata.currency_id or None , line.quantity, product=line.product_id, partner=rowdata.partner_id)
				
				itbis_facturado_price += sum([data['amount'] for data in itbis_facturado_tax_data['taxes']])
				itbis_retenido_price += sum([data['amount'] for data in itbis_retenido_tax_data['taxes']])
				itbis_sujeto_troporcionalidad_price += sum([data['amount'] for data in itbis_sujeto_troporcionalidad_tax_data['taxes']])
				itbis_llevado_price += sum([data['amount'] for data in itbis_llevado_tax_data['taxes']])
				monto_retencion_renta_price += sum([data['amount'] for data in monto_retencion_renta_tax_data['taxes']])
				impuesto_selectivo_al_consumo_price += sum([data['amount'] for data in impuesto_selectivo_al_consumo_tax_data['taxes']])
				otros_impuestos_price += sum([data['amount'] for data in otros_impuestos_tax_data['taxes']])
				monto_propina_legal_price += sum([data['amount'] for data in monto_propina_legal_tax_data['taxes']])

			#11 ITBIS Facturado Taxes total
			worksheet.write(row, col, ("%.2f" % (itbis_facturado_price)).zfill(12))
			col += 1

			#12 itbis_retenido
			itbis_retenido_price = ("%.2f" % (itbis_retenido_price)).zfill(12)
			worksheet.write(row, col, itbis_retenido_price)
			col += 1

			#13
			itbis_sujeto_troporcionalidad_price = ("%.2f" % (itbis_sujeto_troporcionalidad_price)).zfill(12)
			worksheet.write(row, col, itbis_sujeto_troporcionalidad_price)
			col += 1

			#14
			worksheet.write(row, col, ("%.2f" % (itbis_llevado_price)).zfill(12))
			col += 1

			#15
			itbis_price_1 = ("%.2f" % (itbis_facturado_price - itbis_llevado_price)).zfill(12)
			worksheet.write(row, col, itbis_price_1)
			col += 1

			#16
			worksheet.write(row, col, " ")
			col += 1

			#17
			worksheet.write(row, col, " ")
			col += 1

			#18
			monto_retencion_renta_price = ("%.2f" % (monto_retencion_renta_price)).zfill(12)
			worksheet.write(row, col, monto_retencion_renta_price)
			col += 1

			#19
			worksheet.write(row, col, " ")
			col += 1

			#20
			impuesto_selectivo_al_consumo_price = ("%.2f" % (impuesto_selectivo_al_consumo_price)).zfill(12)
			worksheet.write(row, col, impuesto_selectivo_al_consumo_price)
			col += 1

			#21
			otros_impuestos_price = ("%.2f" % (otros_impuestos_price)).zfill(12)
			worksheet.write(row, col, otros_impuestos_price)
			col += 1

			#22
			monto_propina_legal_price = ("%.2f" % (monto_propina_legal_price)).zfill(12)
			worksheet.write(row, col, monto_propina_legal_price)
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

			invoice_ids = self.vendor_bills()

			# for rowdata in self.env['account.invoice'].browse(self._context.get('active_ids')):
			for rowdata in invoice_ids:
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