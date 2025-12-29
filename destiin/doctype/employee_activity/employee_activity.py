# Copyright (c) 2025, shilpa@avohilabs.com and contributors
# For license information, please see license.txt

# import frappe
#from frappe.model.document import Document


#class EmployeeActivity(Document):
#	pass



import frappe
import json
from frappe.model.document import Document

class EmployeeActivity(Document):
    pass


@frappe.whitelist(allow_guest=False)
def get_all_activities():
    """Fetch all Employee Activities"""
    activities = frappe.get_all(
        "Employee Activity",
        fields=["name", "employee", "employee_name", "company", "booking_stage"]
    )
    return activities


@frappe.whitelist(allow_guest=False)
def create_activity():
    """Create a new Employee Activity from raw JSON body"""
    try:
        # Handle both raw JSON and x-www-form-urlencoded inputs
        if frappe.form_dict.get("data"):
            data = json.loads(frappe.form_dict.data)
        elif frappe.request.data:
            data = json.loads(frappe.request.data)
        else:
            frappe.throw("Missing request body")

        doc = frappe.get_doc({
            "doctype": "Employee Activity",
            **data
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": "Employee Activity created successfully",
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_activity API Error")
        return {"success": False, "error": str(e)}
    

@frappe.whitelist(allow_guest=False)
def update_activity():
    """Update only the booking_stage field of Employee Activity by employee_id"""
    try:
        # Handle both raw JSON and x-www-form-urlencoded inputs
        if frappe.form_dict.get("data"):
            data = json.loads(frappe.form_dict.data)
        elif frappe.request.data:
            data = json.loads(frappe.request.data)
        else:
            frappe.throw("Missing request body")

        # Validate required fields
        employee_id = data.get("employee_id")
        booking_stage = data.get("booking_stage")

        if not employee_id:
            frappe.throw("Employee ID is required")
        if booking_stage is None:
            frappe.throw("booking_stage is required")

        # Fetch existing Employee Activity
        existing_doc = frappe.get_all(
            "Employee Activity",
            filters={
           "employee": employee_id,
        "booking_stage": ["!=", "booking_success"]
    	},
            fields=["name"]
        )

        if not existing_doc:
            frappe.throw(f"No Employee Activity found for employee_id: {employee_id}")

        doc_name = existing_doc[0].name
        doc = frappe.get_doc("Employee Activity", doc_name)

        # Update only the booking_stage field
        doc.booking_stage = booking_stage
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": f"Booking stage updated successfully for employee_id {employee_id}",
            "employee_id": employee_id,
            "booking_stage": booking_stage
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_booking_stage API Error")
        return {"success": False, "error": str(e)}