frappe.ui.form.on('Details', {
    refresh: function(frm) {
        // Show "Register" button only if doc is saved
        if (!frm.is_new()) {
            frm.add_custom_button(__('Register'), function() {
                frappe.call({
                    method: "reg.reg.doctype.details.details.register_all",
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint(__('This record has been registered!'));
                        }
                    }
                });
            });
        }
    },

    department: function(frm) {
        if (!frm.doc.department) {
            frm.clear_table("student_details");
            frm.refresh_field("student_details");
            return;
        }

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Students",
                filters: {
                    department: frm.doc.department,
                    register_no: ["=", ""]
                },
                fields: ["name", "name1", "email_id", "phone_no"]
            },
            callback: function(r) {
                if (r.message && r.message.length) {
                    frm.clear_table("student_details");

                    r.message.forEach(function(d) {
                        let row = frm.add_child("student_details");
                        row.student_name = d.name;
                        row.emailid = d.email_id;
                        row.phone_no = d.phone_no;
                    });

                    frm.refresh_field("student_details");
                } else {
                    frappe.msgprint("No students found without Register No in " + frm.doc.department);
                }
            }
        });
    }
});
