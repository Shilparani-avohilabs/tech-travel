import frappe

def ensure_roles_exist():
    """Ensure required roles (Employee, HR Manager) exist."""
    for role in ["Employee", "HR Manager"]:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role
            }).insert(ignore_permissions=True)
            frappe.logger().info(f"✅ Created missing Role: {role}")
    frappe.db.commit()

def execute():
    ensure_roles_exist()

    workflow_name = "Travel Request Approval Workflow"
    doctype = "Travel Request"

    # Define workflow states
    states = [
        {"state": "Draft", "doc_status": 0, "allow_edit": "Employee"},
        {"state": "Pending", "doc_status": 1, "allow_edit": "HR Manager"},
        {"state": "Approved", "doc_status": 1, "allow_edit": "HR Manager"},
        {"state": "Rejected", "doc_status": 1, "allow_edit": "HR Manager"},
    ]

    # Define transitions
    transitions = [
        {"state": "Draft", "action": "Submit", "next_state": "Pending", "allowed": "Employee", "allow_self_approval": 0},
        {"state": "Pending", "action": "Approve", "next_state": "Approved", "allowed": "HR Manager", "allow_self_approval": 0},
        {"state": "Pending", "action": "Reject", "next_state": "Rejected", "allowed": "HR Manager", "allow_self_approval": 0},
    ]

    if frappe.db.exists("Workflow", workflow_name):
        workflow = frappe.get_doc("Workflow", workflow_name)
        # Update missing states
        existing_states = [s.state for s in workflow.states]
        for s in states:
            if s["state"] not in existing_states:
                workflow.append("states", s)
                frappe.logger().info(f"✅ Added missing state: {s['state']}")

        # Update missing transitions
        existing_transitions = [(t.state, t.action) for t in workflow.transitions]
        for t in transitions:
            if (t["state"], t["action"]) not in existing_transitions:
                workflow.append("transitions", t)
                frappe.logger().info(f"✅ Added missing transition: {t['action']} from {t['state']}")

        workflow.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info(f"✅ Updated existing workflow: {workflow_name}")
    else:
        workflow = frappe.get_doc({
            "doctype": "Workflow",
            "workflow_name": workflow_name,
            "document_type": doctype,
            "is_active": 1,
            "override_status": "status",
            "send_email_alert": 0,
            "states": states,
            "transitions": transitions
        })
        workflow.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info(f"✅ Created new workflow: {workflow_name}")
