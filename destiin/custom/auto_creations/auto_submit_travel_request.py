import frappe

def auto_submit_travel_request(doc, method):
    """Auto-submit Travel Request and notify HR Managers when a new request is created."""
    try:
        if doc.docstatus == 0:
            doc.flags.ignore_permissions = True
            doc.submit()
            frappe.db.commit()
            frappe.logger("travel_request", allow_site=True).info(
                f"✅ HRMS Travel Request {doc.name} auto-submitted successfully."
            )
        notify_hr_managers(doc)
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="HRMS Travel Request Auto Submit Error", message=str(e))

def notify_hr_managers(doc):
    """Send notification to all HR/Managers when a Travel Request is submitted."""
    try:
        hr_managers = frappe.get_all(
            "Employee",
            filters={"designation": ["in", ["HR Manager", "Manager"]]},
            fields=["user_id", "employee_name"]
        )
        if not hr_managers:
            frappe.logger("travel_request").info("No HR Managers found to notify.")
            return

        for hr in hr_managers:
            if not hr.user_id:
                continue

            subject = f"New Travel Request Submitted by {doc.employee_name}"
            message = f"🛄 Employee {doc.employee} has submitted a new Travel Request ({doc.name})."

            # Create visible Notification Log entry
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": subject,
                "email_content": message,
                "for_user": hr.user_id,
                "type": "Alert",
                "document_type": "Travel Request",
                "document_name": doc.name
            }).insert(ignore_permissions=True)

        frappe.db.commit()
        frappe.logger("travel_request", allow_site=True).info(
            f"🔔 Notification Logs created for {len(hr_managers)} HR Managers for {doc.name}"
        )
    except Exception as e:
        frappe.log_error(title="HR Manager Notification Error", message=str(e))
