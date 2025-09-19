import asyncio
from playwright.async_api import async_playwright
import frappe


class Students(frappe.model.document.Document):
    pass


SITE_URL = "https://moh.gov.om/en/"

async def submit_google_form(doc):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(SITE_URL, timeout=60000)

            # Step 1: Click "Our Services"
            await page.locator('a.dropdown-toggle:has-text("Our Services")').click()

            # Step 2: Click "Businesses"
            await page.locator('div.col-megamenu >> text=Businesses').click()

            # Step 3: Businesses tab
            await page.locator('a.nav-link:has-text("Businesses")').click()

            # Step 4: Drug Safety Center tab
            await page.locator('button.nav-link:has-text("Drug Safety Center")').click()

            # Step 5: Click "Start Service" (opens a new tab)
            async with context.expect_page() as new_page_info:
                await page.locator(
                    'div.card.eserviceCard:has(h5:has-text("Import Unregistered Medical Devices")) '
                    'a.card-link:has-text("Start Service")'
                ).click()
            new_page = await new_page_info.value
            await new_page.wait_for_load_state("networkidle")

            # Language toggle
            await new_page.locator('a.lang-toggle-switch').click()
            await new_page.wait_for_timeout(2000) 

            # Step 6: Click National ID Login button (use no_wait_after to avoid navigation hang)
            login_button = new_page.locator('a.btn.btn-secondary.btn-sm', has_text="National ID Login")
            await login_button.click(no_wait_after=True)

            print("Clicked on National ID Login button. Waiting for redirection...")

            # Step 7: Wait for SSO redirection
            for _ in range(60):  # up to 60 seconds
                current_url = new_page.url
                if "sso" in current_url or "idp" in current_url or "authentication" in current_url:
                    print("Redirected to SSO page:", current_url)
                    break
                await new_page.wait_for_timeout(1000)
            else:
                raise TimeoutError("Timeout: No SSO redirect detected.")

            # Step 8: Wait for user to complete login
            print("Waiting for user to complete manual login...")

            for _ in range(120):  # up to 2 minutes
                current_url = new_page.url
                if "eportal.moh.gov.om/INRMD" in current_url:
                    print("User completed login:", current_url)
                    break
                await new_page.wait_for_timeout(1000)
            else:
                raise TimeoutError("Timeout: Login not completed.")

            # Optional: Screenshot after login
            await new_page.screenshot(path="after_manual_login.png", full_page=True)

        except Exception as e:
            print("Error occurred:", e)
            try:
                await page.screenshot(path="error_page.png", full_page=True)
                if 'new_page' in locals():
                    await new_page.screenshot(path="error_new_page.png", full_page=True)
            except:
                pass
            raise

        finally:
            await context.close()
            await browser.close()


@frappe.whitelist()
def submit_single_student(docname):
    """Fetch a single Students doc and submit the form"""
    doc = frappe.get_doc("Students", docname)
    asyncio.run(submit_google_form(doc))
    return f"Submitted {docname} successfully!"
