import frappe
import logging

# Initialize frappe logger
logger = frappe.logger("user_creation", allow_site=True, file_count=5)

def create_user_for_manager(doc, method):
    """
    Automatically create or update a User when an Employee with designation
    'Manager' or 'HR Manager' is created or updated.
    """

    try:
        # Only handle Manager or HR Manager designations
        if doc.designation not in ["Manager", "HR Manager"]:
            logger.info(f"Skipped Employee '{doc.name}' — Designation: {doc.designation}")
            return

        # Prefer company_email, fallback to personal_email
        user_email = doc.company_email or doc.personal_email
        if not user_email:
            logger.warning(f"No email found for Employee '{doc.name}'. Skipping user creation/update.")
            return

        # Determine the correct role
        role_name = "Manager" if doc.designation == "Manager" else "HR Manager"

        # Verify that the Role exists in system
        if not frappe.db.exists("Role", role_name):
            logger.error(f"Role '{role_name}' not found. Please create it in the Role List.")
            frappe.throw(f"Role '{role_name}' does not exist. Please create it in the Role List.")
            return

        # Check if user already exists
        user_name = frappe.db.exists("User", {"email": user_email})

        if user_name:
            # ✅ User exists — update their name and roles if necessary
            user = frappe.get_doc("User", user_name)
            updated = False

            # Update first name if changed
            if user.first_name != doc.employee_name:
                logger.info(f"Updating name for user '{user_email}' to '{doc.employee_name}'")
                user.first_name = doc.employee_name
                updated = True

            # Check if correct role already exists
            role_exists = any(r.role == role_name for r in user.roles)
            if not role_exists:
                logger.info(f"Updating roles for user '{user_email}' to '{role_name}'")
                user.roles = [r for r in user.roles if r.role not in ["Manager", "HR Manager"]]
                user.append("roles", {"role": role_name})
                updated = True

            if updated:
                user.save(ignore_permissions=True)
                frappe.db.commit()
                logger.info(f"Existing user '{user_email}' updated successfully.")
            else:
                logger.info(f"User '{user_email}' already up-to-date.")
            return

        # 🆕 Create new user if not exists
        user = frappe.get_doc({
            "doctype": "User",
            "email": user_email,
            "first_name": doc.employee_name,
            "send_welcome_email": 1,
            "enabled": 1,
            "roles": [{"role": role_name}]
        })

        user.insert(ignore_permissions=True)
        frappe.db.commit()

        logger.info(f"New user created successfully for '{doc.employee_name}' ({user_email})")

    except Exception as e:
        frappe.db.rollback()
        logger.exception(f"Error while creating/updating user for Employee '{doc.name}': {str(e)}")
