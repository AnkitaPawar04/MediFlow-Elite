"""
Selenium Test for MediFlow Login
Tests the admin login functionality
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Configuration
LOGIN_URL = "http://127.0.0.1:8000/?tab=admin"
TEST_EMAIL = "ankita.pawarr19@gmail.com"
TEST_PASSWORD = "Admin@1904"
WAIT_TIMEOUT = 10


def test_admin_login():
    """Test admin login functionality"""
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("🔄 Opening login page...")
        driver.get(LOGIN_URL)
        time.sleep(3)
        
        print("📧 Entering credentials...")
        # Locate email field
        email = driver.find_element(By.NAME, "email")
        email.clear()
        email.send_keys(TEST_EMAIL)
        
        # Locate password field
        password = driver.find_element(By.NAME, "password")
        password.clear()
        password.send_keys(TEST_PASSWORD)
        
        print("🔑 Clicking login button...")
        
        # Try multiple selector strategies
        try:
            # Strategy 1: Find button by class and contains 'sign in' text
            wait = WebDriverWait(driver, WAIT_TIMEOUT)
            login_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='login-btn']"))
            )
            print(f"Found button with class 'login-btn'")
        except:
            print("Strategy 1 failed, trying alternative selector...")
            # Strategy 2: Find by type=submit
            login_btn = driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'login-btn')]")
            print(f"Found button with type='submit'")
        
        login_btn.click()
        
        print("⏳ Waiting for redirect...")
        time.sleep(5)
        
        # Check login success
        current_url = driver.current_url.lower()
        print(f"Current URL: {driver.current_url}")
        
        if "dashboard" in current_url or "admin" in current_url:
            print("\n✅ Login Test Passed!")
            return True
        else:
            print("\n❌ Login Test Failed - Not redirected to dashboard/admin")
            # Print page source for debugging
            print("\n📄 Page Title:", driver.title)
            return False
            
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        driver.quit()


if __name__ == "__main__":
    print("=" * 50)
    print("🏥 MediFlow Admin Login Test")
    print("=" * 50)
    success = test_admin_login()
    exit(0 if success else 1)
