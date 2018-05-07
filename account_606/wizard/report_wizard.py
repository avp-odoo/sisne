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
	invoice_data = fields.Char('Name')
	file_name = fields.Binary('Invoice Report', readonly=True)
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
			if company.vat and len(company.vat) == 11:
				rnc = company.vat

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
				rnc = rowdata.partner_id.vat and rowdata.partner_id.vat.zfill(9) or ''
			else:
				rnc = rowdata.partner_id.vat and rowdata.partner_id.vat.zfill(11) or ''

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
			worksheet.write(row, col, rowdata.ncf)
			col += 1
			
			#5
			worksheet.write(row, col, rowdata.ncf_modification)
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
		
		out = base64.encodestring(data)

		attach_vals = {'invoice_data': f_name, 'file_name': out}
		act_id = self.env['account.invoice.report.service.606'].create(attach_vals)
		return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.report.service.606',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }

	@api.multi
	def print_text_report_custom(self):
		try:
			file_name = '606'
			if self.year:
				file_name = file_name + str(self.year)

			if self.month:
				file_name = file_name + str(self.month)

			name = file_name + '.txt'  # Name of text file coerced with +.txt
			file = open(name,'w+')   # Trying to create a new file or open one

			user_id = self.env.user
			company_id = user_id.company_id

			invoice_ids = self.vendor_bills()

			### Header Part ###
			header_1 = self._remove_ascii_char('Código Información')
			header_2 = self._remove_ascii_char('RNC o Cédula')
			header_3 = self._remove_ascii_char('Periodo')
			header_4 = self._remove_ascii_char('Cantidad Registros')

			header_string = header_1 + " | " + header_2 + " | " + header_3 + " | " + header_4 + "\n"
			file.write(header_string)

			# Company Detail
			rnc_no = ''
			if self.env.user and self.env.user.company_id:
				company = self.env.user.company_id
				if company.vat and len(company.vat) == 11:
					rnc_no = company.vat

			header_val_1 = "{:>18}".format(str("606"))
			header_val_2 = "{:>12}".format(str(rnc_no))
			header_val_3 = "{:>7}".format(str(self.year) + str(self.month))
			header_val_4 = "{:>18}".format(str(len(invoice_ids)))

			header_val_string = header_val_1 + " | " + header_val_2 + " | " + header_val_3 + " | " + header_val_4 + "\n\n\n"

			file.write(header_val_string)

			inv_header_1 = self._remove_ascii_char('RNC o Cédula')
			inv_header_2 = 'Tipo Id'
			inv_header_3 = self._remove_ascii_char('Tipo Bienes y Servicios Comprados')
			inv_header_4 = 'NCF'
			inv_header_5 = 'NCF Documento Modificado'
			inv_header_6 = 'Fecha Comprobante'
			inv_header_7 = 'Fecha Pago'
			inv_header_8 = 'Monto Facturado en Servicios'
			inv_header_9 = 'Monto Facturado en Bienes'
			inv_header_10 = 'Total Monto Facturado'
			inv_header_11 = 'ITBIS Facturado'
			inv_header_12 = 'Itbis Retenido'
			inv_header_13 = 'ITBIS sujeto a Proporcionalidad (Art. 349)'
			inv_header_14 = 'ITBIS llevado al Costo'
			inv_header_15 = 'ITBIS por Adelantar'
			inv_header_16 = 'ITBIS percibido en compras'
			inv_header_17 = self._remove_ascii_char('Tipo de Retención en ISR')
			inv_header_18 = self._remove_ascii_char('Monto Retención Renta')
			inv_header_19 = 'ISR Percibido en compras'
			inv_header_20 = 'Impuesto Selectivo al Consumo'
			inv_header_21 = 'Otros Impuestos/Tasas'
			inv_header_22 = 'Monto Propina Legal'
			inv_header_23 = 'Forma de Pago'

			inv_header_string = inv_header_1 + " | " + inv_header_2 + " | " + inv_header_3 + " | " + inv_header_4 + " | " \
			+ inv_header_5 + " | " + inv_header_6 + " | " + inv_header_7 + " | " + inv_header_8 + " | " + inv_header_9 + " | " \
			+ inv_header_10 + " | " + inv_header_11 + " | " + inv_header_12 + " | " + inv_header_13 + " | " \
			+ inv_header_14 + " | " + inv_header_15 + " | " + inv_header_16 + " | " + inv_header_17 + " | " \
			+ inv_header_18 + " | " + inv_header_19 + " | " + inv_header_20 + " | " + inv_header_21 + " | " \
			+ inv_header_22 + " | " + inv_header_23 + "\n"

			file.write(inv_header_string)

			length = len(invoice_ids)
			for rowdata in invoice_ids:
				rnc = ''
				if rowdata.partner_id and rowdata.partner_id.is_company:
					rnc = "{:>9}".format(str(rowdata.partner_id.vat or ''))
				else:
					rnc = "{:>11}".format(str(rowdata.partner_id.vat or ''))

				inv_val_1 = rnc
				inv_val_2 = rowdata.tipo_id
				inv_val_3 = rowdata.tipo
				inv_val_4 = "{:>11}".format(str(rowdata.ncf))
				inv_val_5 = "{:>19}".format(str(rowdata.ncf_modification))
				inv_val_6 = datetime.datetime.strptime(rowdata.date_invoice, '%Y-%m-%d').strftime('%Y%m%d')

				#7
				pay_date = ""
				if rowdata.pay_year and rowdata.pay_date:
					pay_date = rowdata.pay_year + rowdata.pay_date
				
				inv_val_7 = "{:>6}".format(str(pay_date))
				
				#8 Total of service type product without tax
				total_monto_facturado_en_servicios = sum([line.quantity * line.price_unit for line in rowdata.invoice_line_ids if line.product_id and line.product_id.type == 'service'])
				inv_val_8 = "%012.2f" % (total_monto_facturado_en_servicios,) 
				
				# #9 Total of not service type product without tax
				total_monto_facturado_en_bienes = sum([line.quantity * line.price_unit for line in rowdata.invoice_line_ids if line.product_id and line.product_id.type != 'service'])
				inv_val_9 = "%012.2f" % (total_monto_facturado_en_bienes,) 

				#10 Total amount without tax
				inv_val_10 = "%012.2f" % (rowdata.amount_untaxed,)

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
				
				inv_val_11 = "%012.2f" % (itbis_facturado_price,)
				inv_val_12 = "%012.2f" % (itbis_retenido_price,)
				inv_val_13 = "%012.2f" % (itbis_sujeto_troporcionalidad_price,)
				inv_val_14 = "%012.2f" % (itbis_llevado_price,)
				inv_val_15 = "%012.2f" % ((itbis_facturado_price - itbis_llevado_price),)
				inv_val_16 = "%012.2f" % (0,)
				inv_val_17 = "{:>2}".format(str(''))
				inv_val_18 = "%012.2f" % (monto_retencion_renta_price,)
				inv_val_19 = "%012.2f" % (0,)
				inv_val_20 = "%012.2f" % (impuesto_selectivo_al_consumo_price,)
				inv_val_21 = "%012.2f" % (otros_impuestos_price,)
				inv_val_22 = "%012.2f" % (monto_propina_legal_price,)
				inv_val_23 = "{:>2}".format(str(''))

				inv_val_string = str(inv_val_1) + " | " + str(inv_val_2) + " | " + str(inv_val_3) + " | " + str(inv_val_4) + " | " + str(inv_val_5) \
					+ " | " + str(inv_val_6) + " | " + str(inv_val_7) + " | " + str(inv_val_8) + " | " + str(inv_val_9) + " | " + str(inv_val_10) \
					+ " | " + str(inv_val_11) + " | " + str(inv_val_12) + " | " + str(inv_val_13) + " | " + str(inv_val_14) + " | " + str(inv_val_15) \
					+ str(inv_val_16) + " | " + str(inv_val_17) + " | " + str(inv_val_18) + " | " + str(inv_val_19) + " | " + str(inv_val_20) + " | " \
					+ str(inv_val_21) + " | " + str(inv_val_22) + " | " + str(inv_val_23)

				if length > 1:
					inv_val_string += "\n"
					length -= 1
				file.write(inv_val_string)
			file.close()
		except:
			print('Something went wrong! Can\'t tell what?', sys.exc_info()[0])
			sys.exit(0) # quit Python
		with open(name, 'r') as myfile:
			data = myfile.read()
			myfile.close()
			result = base64.b64encode(data)
		
		attach_vals = {'invoice_data': name, 'file_name': result}
		act_id = self.env['account.invoice.report.service.606'].create(attach_vals)
		return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.report.service.606',
            'res_id': act_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }

