import pytest
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
# --- Import Edge-specific classes ---
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# --- Pytest Fixtures ---
# Set up and tear down resources for your tests.
@pytest.fixture(scope="module")
def app_server():
    """
    Fixture to start and stop the Streamlit app server
    in a separate process.
    """
    # Start the Streamlit app on a specific port
    port = "8511"
    url = f"http://localhost:{port}"

    # Use subprocess.Popen to run Streamlit in the background
    try:
        proc = subprocess.Popen(
            ["streamlit", "run", "app.py", "--server.port", port, "--server.headless", "true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Give the server a few seconds to boot up
        time.sleep(5)

        # Yield the URL to the test function
        yield url

    finally:
        # Teardown: stop the server after the test is done
        proc.kill()


@pytest.fixture(scope="module")
def driver():
    """Fixture to set up and tear down the Selenium WebDriver."""
    options = EdgeOptions()
    options.use_chromium = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # --- Hardcoded driver for local run without internet connection for a driver manager ---
    service = EdgeService(executable_path=r"../msedgedriver.exe")

    driver_instance = webdriver.Edge(service=service, options=options)
    yield driver_instance
    driver_instance.quit()


# --- Parameterized Test Cases ---
# Each tuple contains the parameters for one full test run.
test_cases = [
    # (test_id, lang_btn, accept_btn, lottery_btn, num_clicks, submit_btn, result_header, success_msg_part)
    ('hu5_en', 'English', '✅ I Accept', 'Ötöslottó', 5, 'Submit', '🎯 Lottery Results', 'You won'),
    ('hu6_en', 'English', '✅ I Accept', 'Hatoslottó', 6, 'Submit', '🎯 Lottery Results', 'You won'),
    ('hu7_en', 'English', '✅ I Accept', 'Skandináv lottó', 7, 'Submit', '🎯 Lottery Results', 'You won'),
    ('hu5_hu', 'Magyar', '✅ Elfogadom', 'Ötöslottó', 5, 'Lássuk!', '🎯 Találatok', 'esetben volt találatod! 🎉'),
    ('hu6_hu', 'Magyar', '✅ Elfogadom', 'Hatoslottó', 6, 'Lássuk!', '🎯 Találatok', 'esetben volt találatod! 🎉'),
    ('hu7_hu', 'Magyar', '✅ Elfogadom', 'Skandináv lottó', 7, 'Lássuk!', '🎯 Találatok', 'esetben volt találatod! 🎉'),
]

@pytest.mark.parametrize(
    "test_id, lang_btn, accept_btn, lottery_btn, num_clicks, submit_btn, result_header, success_msg_part",
    test_cases,
    ids=[case[0] for case in test_cases]  # Use test_id for clean pytest output
)
def test_full_user_journey(
    app_server, driver,
    test_id, lang_btn, accept_btn, lottery_btn, num_clicks, submit_btn, result_header, success_msg_part
):
    """
    Tests the full user flow using parameterized inputs.
    """

    # Get the URL from the app_server fixture
    driver.get(app_server)

    # Set a 10-second wait time for elements to appear
    wait = WebDriverWait(driver, 10)

    try:
        # --- 1. Welcome Page ---
        # Find and click the language button
        lang_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button//*[text()='{lang_btn}']"))
        )
        lang_button.click()

        # --- 2. Disclaimer Page ---
        # Wait for the 'I Accept' button to appear and click it
        accept_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button//*[text()='{accept_btn}']"))
        )
        accept_button.click()

        # --- 3. Selector Page ---
        # Wait for the lottery button to appear and click it
        lottery_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button//*[text()='{lottery_btn}']"))
        )
        lottery_button.click()

        # --- 4. Number Picker Page ---
        # Wait for the number grid to be visible
        wait.until(
            EC.visibility_of_element_located((By.XPATH, "//button//*[text()='1']"))
        )

        # Click on the required number of numbers
        for i in range(1, num_clicks + 1):
            driver.find_element(By.XPATH, f"//button//*[text()='{i}']").click()
            time.sleep(0.1)  # Small pause to register the click

        # Find and click the 'Submit' button
        submit_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button//*[text()='{submit_btn}']"))
        )
        submit_button.click()

        # --- 5. Results Page ---
        # Wait for the results header to appear
        results_header_el = wait.until(
            EC.visibility_of_element_located((By.XPATH, f"//h2[contains(., '{result_header}')]"))
        )

        # Assert that the header is displayed
        assert results_header_el.is_displayed()

        # Check for the success message
        success_message = wait.until(
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{success_msg_part}')]"))
        )
        assert success_message.is_displayed()

    except Exception as e:
        raise e

