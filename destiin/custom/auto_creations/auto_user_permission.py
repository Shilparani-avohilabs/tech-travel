import frappe

def create_user_permission_for_hr_manager(doc, method):
    """Automatically create or update User Permission for HR Managers based on their company."""
    try:
        if doc.designation != "HR Manager":
            return

        if not doc.user_id or not doc.company:
            frappe.logger("user_permission").info(f"Skipping {doc.name}: Missing user_id or company.")
            return

        existing = frappe.db.exists(
            "User Permission",
            {"user": doc.user_id, "allow": "Company"}
        )

        if existing:
            permission = frappe.get_doc("User Permission", existing)
            if permission.for_value != doc.company:
                permission.for_value = doc.company
                permission.save(ignore_permissions=True)
                frappe.logger("user_permission").info(
                    f"🔄 Updated User Permission for {doc.user_id} to {doc.company}"
                )
        else:
            permission = frappe.get_doc({
                "doctype": "User Permission",
                "user": doc.user_id,
                "allow": "Company",
                "for_value": doc.company,
                "apply_to_all_doctypes": 0
            })
            permission.insert(ignore_permissions=True)
            frappe.logger("user_permission").info(
                f"✅ Created User Permission for {doc.user_id} ({doc.company})"
            )

        frappe.db.commit()

    except Exception as e:
        frappe.log_error(title="HR Manager User Permission Error", message=str(e))
