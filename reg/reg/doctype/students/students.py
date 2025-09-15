import asyncio
from playwright.async_api import async_playwright
import frappe


class Students(frappe.model.document.Document):
    pass



FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdnz2VZUS5tDSIwBUwFe4T9W6EyEHTvtGXT7mO4B_hhRXYuDA/viewform?usp=sharing&ouid=117504253436019035250"

async def submit_google_form(doc):
    """Submit a single Students record via Playwright to Google Form"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(FORM_URL)

        # Fill all fields using .fill()
        await page.get_by_label('Name').fill(doc.name1)
        await page.get_by_label("Department").click()  # Wait a moment for options to render (sometimes necessary for Google Forms)
        await page.wait_for_timeout(500)
        await page.get_by_role("option", name=doc.department).click()
        await page.get_by_label('Phone No').fill(doc.phone_no)       # Click submit
        await page.get_by_role('button', name='Submit').click()

        await browser.close()
        frappe.logger().info(f"Submitted {doc.name1} successfully.")


@frappe.whitelist()
def submit_single_student(docname):
    """Fetch a single Students doc and submit the form"""
    doc = frappe.get_doc("Students", docname)
    asyncio.run(submit_google_form(doc))
    return f"Submitted {docname} successfully!"
