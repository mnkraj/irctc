import streamlit as st
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import cv2
import pytesseract
import numpy as np
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
user_id = os.getenv("id")
password = os.getenv("password")

# Selenium WebDriver setup
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")

service = Service()

# Function to handle login
def login(id, pwd):
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.irctc.co.in/nget/train-search")
    try:
        # Click on the login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "LOGIN"))
        )
        login_button.click()

        # Enter user credentials
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='User Name']"))
        ).send_keys(id)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Password']"))
        ).send_keys(pwd)

        # Handle CAPTCHA
        while True:
            try:
                captcha_image = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".captcha-img"))
                )

                captcha_src = captcha_image.get_attribute("src")
                base64_data = captcha_src.split(",")[1]
                image_data = base64.b64decode(base64_data)
                np_arr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                captcha_input_user = pytesseract.image_to_string(image).strip()
                st.write(f"Detected CAPTCHA: {captcha_input_user}")

                # Enter CAPTCHA and attempt login
                captcha_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter Captcha']"))
                )
                captcha_input.send_keys(captcha_input_user)

                submit_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='SIGN IN']"))
                )
                submit_btn.click()

                # Check if login is successful
                WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Logout']"))
                )
                st.success("Login successful!")
                driver.close()
                return True
            except Exception:
                st.warning("Invalid CAPTCHA. Retrying...")
                continue
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        driver.quit()

# Streamlit App Interface
st.title("IRCTC Login Automation")

if st.button("Start"):
    if user_id and password:
        st.write("Starting the login process...")
        login(user_id, password)
    else:
        st.error("User ID or Password is not set in the .env file.")
