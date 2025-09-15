import asyncio
from playwright.async_api import async_playwright
import frappe
from frappe.model.document import Document

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdnz2VZUS5tDSIwBUwFe4T9W6EyEHTvtGXT7mO4B_hhRXYuDA/viewform?usp=header"

class Details(Document):
    pass

async def submit_google_form(page, rec):
    try:
        await page.goto(FORM_URL)
        await page.get_by_label('Name').fill(rec["student_name"])   # Name field
        await page.get_by_label('Phone No').fill(rec["phone_no"]) 

        await page.locator("div[role='listbox']").click()
        await page.wait_for_selector(f"div[role='option'][data-value='{rec['department']}']", timeout=2000)
        await page.locator(f"div[role='option'][data-value='{rec['department']}']").click()

                   
        await page.wait_for_timeout(1000) 
        await page.get_by_role('button', name='Submit').click() # wait for submission
        await page.wait_for_timeout(1000)
        

        return True

    except Exception as e:
        print(f"Error submitting form: {e}")
        return False


@frappe.whitelist()
def register_all(docname):
    """Submit all student_details rows for a Details doc"""

    async def process():
        doc = frappe.get_doc("Details", docname)
        success, failed = 0, 0

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # set headless=True for production
            context = await browser.new_context()
            page = await context.new_page()
            department = doc.department

            for row in doc.student_details:
                rec = {
                    "student_name": row.student_name,
                    "department":department,
                    "phone_no": row.phone_no,
                }

                ok = await submit_google_form(page, rec)
                if ok:
                    success += 1
                else:
                    failed += 1

            await browser.close()

        return success, failed

    # Run inside Frappe worker thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success, failed = loop.run_until_complete(process())
    loop.close()

    frappe.msgprint(f"Finished submission →  {success} success,  {failed} failed")
    return {"status": "done", "submitted": success, "failed": failed}
