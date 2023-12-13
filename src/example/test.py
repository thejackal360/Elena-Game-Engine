#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import subprocess
import time


def start_web_server():
    subprocess.run(["python3.10", "app.py", "--local"])


def run_playwright_test():

    # Step 3: Launch a browser and open a new page
    print("Step 3: Launching browser and opening a new page...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Step 4: Navigate to the web page
        print("Step 4: Navigating to the web page...")
        page.goto("http://127.0.0.1:5000/")
        print("Page loaded!")
        page.wait_for_timeout(4000)

        # Step 5: Find and click on the "Bacterial Culture" bubble
        bacterial_culture_bubble = page.locator("p#Bacterial_Culture")
        print("Step 5: Clicking 'Bacterial Culture' bubble...")
        bacterial_culture_bubble.focus()
        page.wait_for_timeout(4000)
        page.keyboard.press("Enter")
        print("Successfully clicked 'Bacterial Culture'!")

        # Step 6: Find and click on the "Start Prelab" button
        start_prelab_button = page.locator("p#start_prelab_button")
        print("Step 6: Clicking 'Start Prelab' button...")
        page.wait_for_timeout(4000)
        start_prelab_button.click(force=True)
        print("Successfully clicked 'Start Prelab' button!")
        page.wait_for_timeout(15000)

        # Step 7: Type "Joseph" as the user's name and press Enter
        print("Step 7: Typing 'Joseph' and pressing Enter...")
        for char in "Joseph":
            page.keyboard.press(char)
        page.keyboard.press("Enter")
        page.wait_for_timeout(10000)

        # Step 8: Add additional Playwright actions or assertions as needed

        # Step 9: Close the browser
        print("Step 9: Closing the browser...")
        browser.close()


if __name__ == "__main__":
    import multiprocessing

    # Step 1: Start the web server in a separate process
    print("Step 1: Starting web server...")
    web_server_process = multiprocessing.Process(target=start_web_server)
    web_server_process.start()

    # Step 2: Wait for the server to start (adjust sleep time as needed)
    print("Step 2: Waiting for the server to start...")
    time.sleep(5)

    try:
        # Run the Playwright test in the main process
        run_playwright_test()
    finally:
        # Step 10: Stop the web server process when the test is done
        print("Step 10: Stopping web server process...")
        web_server_process.terminate()
        web_server_process.join()
        print("Test complete.")
