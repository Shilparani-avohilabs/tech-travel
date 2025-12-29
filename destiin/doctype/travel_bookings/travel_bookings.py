# Copyright (c) 2025, shilpa@avohilabs.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TravelBookings(Document):
    pass


@frappe.whitelist(allow_guest=False)
def get_all_bookings():
    import json
    """Fetch all travel bookings for a specific employee"""
    try:
        # Handle both form and JSON request payloads
        if frappe.form_dict.get("data"):
            data = json.loads(frappe.form_dict.data)
        elif frappe.request.data:
            data = json.loads(frappe.request.data)
        else:
            frappe.throw("Missing request body")

        employee_id = data.get("employee_id")
        if not employee_id:
            frappe.throw("Employee ID is required")

        bookings = frappe.get_all(
            "Travel Bookings",
            filters={"employee_id": employee_id},  # or "employee_id" if your field is named that way
            fields=[
                "name",
                "employee_name",
                "booking_id",
                "hotel_name",
                "check_in_date",
                "check_out_date",
                "booking_status"
            ],
            order_by="check_in_date desc"
        )

        return {
            "success": True,
            "count": len(bookings),
            "data": bookings
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_all_bookings API Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def create_booking():
    """Create a new booking"""
    import json
    try:
        # Handle both raw JSON and x-www-form-urlencoded inputs
        if frappe.form_dict.get("data"):
            data = json.loads(frappe.form_dict.data)
        elif frappe.request.data:
            data = json.loads(frappe.request.data)
        else:
            frappe.throw("Missing request body")
        # data = json.loads(data) if isinstance(data, str) else data
        doc = frappe.get_doc({
            "doctype": "Travel Bookings",
            **data
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {
            "success": True,
            "message": "Booking created successfully",
            "name": doc.name
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_booking API Error")
        return {"success": False, "error": str(e)}
    



@frappe.whitelist(allow_guest=False)
def update_booking():
    """Update an existing booking based on employee_id"""
    import json
    try:
        # Handle both raw JSON and x-www-form-urlencoded inputs
        if frappe.form_dict.get("data"):
            data = json.loads(frappe.form_dict.data)
        elif frappe.request.data:
            data = json.loads(frappe.request.data)
        else:
            frappe.throw("Missing request body")

        # Extract employee_id
        employee_id = data.get("employee_id")
        if not employee_id:
            frappe.throw("Employee ID is required")

        # Find booking by employee_id
        booking_name = frappe.db.get_value("Travel Bookings", {"employee_id": employee_id}, "name")
        if not booking_name:
            return {"success": False, "message": f"No booking found for Employee ID: {employee_id}"}

        # Load and update the booking
        doc = frappe.get_doc("Travel Bookings", booking_name)
        doc.update(data)
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": f"Booking for Employee ID {employee_id} updated successfully",
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_booking API Error")
        return {"success": False, "error": str(e)}
