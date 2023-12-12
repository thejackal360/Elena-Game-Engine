#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import subprocess
import time


def start_web_server():
    subprocess.run(["python3.10", "app.py", "--local"])


def run_playwright_test():
    with sync_playwright() as p:
        # Wait for the server to start (adjust sleep time as needed)
        time.sleep(5)

        # Launch a browser and open a new page
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the web page
        print("Loading page...")
        page.goto("http://127.0.0.1:5000/")
        print("Page loaded!")
        page.wait_for_timeout(4000)

        # Find and click on the "Bacterial Culture" bubble
        bacterial_culture_bubble = page.locator("p#Bacterial_Culture")
        print("Attempting to click 'Bacterial Culture' bubble...")
        print(bacterial_culture_bubble)
        bacterial_culture_bubble.focus()
        page.wait_for_timeout(4000)
        page.keyboard.press("Enter")
        print("Successfully clicked 'Bacterial Culture'!")
        start_prelab_button = page.locator("p#start_prelab_button")
        print(start_prelab_button)
        page.wait_for_timeout(4000)
        start_prelab_button.click(force=True)
        print("Successfully clicked 'Start Prelab' button!")
        page.wait_for_timeout(15000)
        for char in "Joseph":
            page.keyboard.press(char)
        page.keyboard.press("Enter")
        page.wait_for_timeout(10000)

        # Add additional Playwright actions or assertions as needed

        # Close the browser
        browser.close()


if __name__ == "__main__":
    import multiprocessing

    # Start the web server in a separate process
    web_server_process = multiprocessing.Process(target=start_web_server)
    web_server_process.start()

    try:
        # Run the Playwright test in the main process
        run_playwright_test()
    finally:
        # Stop the web server process when the test is done
        web_server_process.terminate()
        web_server_process.join()
