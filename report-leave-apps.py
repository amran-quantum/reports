# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
from erpnext.payroll.report.salary_register.salary_register import get_columns
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []

	columns, leave_types = get_columns()
	fdata = get_data(filters)
	for item in fdata:
		row = [item.employee_name]

		for e in leave_types:
			leave_application = frappe.get_list('Leave Application',
			filters={"employee_name": item.employee_name,
						"status": "Approved",
						"leave_type": e,
						"from_date": ['>=', filters.from_date],
						"to_date": ['<=', filters.to_date]},
			fields={"total_leave_days"}
						)
			leave_details = frappe.db.sql("""select * from `tabLeave Type` where leave_type_name=%(ltn)s""",{"ltn":e},as_dict=1)
			if len(leave_application)> 0: 			
				total = leave_details[0].max_leaves_allowed
				taken = 0

				for elem in leave_application:
					taken += elem.total_leave_days
				remaining = total - taken
				row.append(total)
				row.append(taken)
				row.append(remaining)
			else:
				leave_allocation = frappe.db.count('Leave Allocation', {'employee_name':item.employee_name,'leave_type':e })


				if leave_allocation > 0:
					row.append(leave_details[0].max_leaves_allowed)
				else:
					row.append(0)
				row.append(0)
				row.append(0)
					
		data.append(row)
	return columns, data


def get_columns():
	columns = [
		 _("Employee Name") + "::140"
	]
	leave_types = {_("lt_list"): []}
	leave_allocation = frappe.db.sql("""select distinct leave_type from `tabLeave Allocation`""",as_dict=1)
	for component in frappe.db.sql("""select leave_type_name from `tabLeave Type` where leave_type_name in (%s)"""%
		(', '.join(['%s']*len(leave_allocation))), tuple([d.leave_type for d in leave_allocation]),as_dict=1):
		leave_types[_("lt_list")].append(component.leave_type_name)
	
	columns = columns + [(e +" "+ f + "::120") for e in leave_types[_("lt_list")] for f in ["Total","Taken","Remaining"] ]

	return columns, leave_types[_("lt_list")]


def get_data(filters):
	data = frappe.db.sql(
		"""
		select distinct employee_name from `tabLeave Allocation` where from_date>=%(from_date)s and to_date<=%(to_date)s
		"""
	,{"from_date":filters.from_date, "to_date":filters.to_date},as_dict=1)
	
	return data

	


