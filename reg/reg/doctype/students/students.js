frappe.ui.form.on("Students", {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button("Register", function() {
                frappe.call({
                    method: "reg.reg.doctype.students.students.submit_single_student",
                    args: { docname: frm.doc.name },
                    callback: function(r) {
                        frappe.msgprint(r.message);
                    },
                    error: function(err) {
                        frappe.msgprint("Error submitting Google Form: " + err.message);
                    }
                });
            });
        }
    }
});
