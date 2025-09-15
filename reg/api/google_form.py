async def submit_google_form(name, department, phone_no):
    """Submit a single student row to Google Form"""
    try:
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=False)  # Set to True after testing
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(FORM_URL)
            await page.wait_for_timeout(3000)  # Allow the form to load

            # Get all input fields (Google Forms uses this order based on creation)
            inputs = page.locator('input[type="text"]')
            await inputs.nth(0).fill(name)        # Name
            await inputs.nth(1).fill(department)  # Department
            await inputs.nth(2).fill(phone_no)    # Phone No

            # Submit button
            await page.locator('div[role="button"]:has-text("Submit")').click()

            # Optional: Wait for the "response recorded" confirmation
            await page.wait_for_timeout(2000)

            await browser.close()
            frappe.msgprint(f"Submitted: {name}, {department}, {phone_no}") 
            frappe.logger().info(f"Submitted: {name}, {department}, {phone_no}")

    except Exception as e:
        frappe.log_error(str(e), f"Submission failed for: {name}")
