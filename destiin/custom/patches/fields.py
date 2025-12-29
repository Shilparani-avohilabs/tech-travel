import frappe

def execute():
    # Check if the Custom Field already exists
    if not frappe.db.exists("Custom Field", {"dt": "Travel Request", "fieldname": "amount"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Travel Request",
            "fieldname": "amount",
            "label": "Amount",
            "fieldtype": "Currency",
            "insert_after": "purpose_of_travel",  # adjust if needed
            "description": "Total travel amount or estimated cost"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info("✅ Added 'Amount' field to Travel Request")


    if not frappe.db.exists("Custom Field", {"dt": "Travel Request", "fieldname": "status"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Travel Request",
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Select",
            "options": "Pending\nApproved\nRejected",
            "default": "Pending",
            "insert_after": "amount",  # Place it right after amount
            "description": "Status of the travel request (Pending, Approved, or Rejected)"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info("✅ Added 'Status' field to Travel Request")
    
    
   # Room Type field
    if not frappe.db.exists("Custom Field", {"dt": "Travel Request", "fieldname": "room_type"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Travel Request",
            "fieldname": "room_type",
            "label": "Room Type",
            "fieldtype": "Data",
            "insert_after": "amount",  # Adjust based on your layout
            "description": "Type of room booked or requested (e.g., Single, Double, Suite)"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info("✅ Added 'Room Type' field to Travel Request")
