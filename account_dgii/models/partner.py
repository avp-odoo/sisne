# -*- coding: utf-8 -*-

from openerp import api, fields, models, _

class ResPartner(models.Model):
	_inherit = "res.partner"

	rnc = fields.Char(string="RNC",size=9)
	cedula = fields.Char(string="Cedula",size=11)  

class ResCompany(models.Model):
	_inherit = 'res.company'

	rnc_no = fields.Char(string="RNC",size=11)
	