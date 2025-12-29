"""
🌐 Browser Embassy - דפדפן שגרירותי על HuggingFace Spaces
===========================================================

דפדפן מלא עם Selenium שרץ בענן, ללא NetFree!
API מלא לשליטה מרחוק, screenshots, ומילוי טפסים.

Author: Embassy V4 Architecture
"""

from flask import Flask, request, jsonify, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import os
import time
import base64
from io import BytesIO
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global browser instance
driver = None

def init_browser():
    """
    אתחול דפדפן Chrome עם Selenium
    """
    global driver
    
    if driver is not None:
        logger.info("Browser already initialized")
        return driver
    
    logger.info("Initializing Chrome browser...")
    
    options = Options()
    options.add_argument('--headless=new')  # רץ ברקע (גרסה חדשה)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # התעלם משגיאות SSL (למקרה ש-Oracle יש בעיות)
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-insecure-localhost')
    
    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # נסה למצוא ChromeDriver
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        logger.warning(f"Failed with default ChromeDriver: {e}")
        # נסה עם Remote WebDriver (לתמונות Selenium)
        from selenium.webdriver import Remote
        driver = Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=options
        )
    driver.set_page_load_timeout(30)
    
    logger.info("✅ Chrome browser initialized!")
    return driver


@app.route('/')
def home():
    """
    דף בית
    """
    return jsonify({
        "service": "Browser Embassy V4",
        "status": "operational",
        "description": "Remote browser automation service",
        "endpoints": {
            "/navigate": "Navigate to URL",
            "/screenshot": "Get current page screenshot",
            "/extract_fields": "Extract form fields",
            "/fill_field": "Fill a form field",
            "/click": "Click an element",
            "/get_html": "Get page HTML",
            "/execute_js": "Execute JavaScript",
            "/status": "Browser status"
        }
    })


@app.route('/status')
def status():
    """
    בדיקת סטטוס הדפדפן
    """
    global driver
    
    if driver is None:
        return jsonify({
            "browser": "not_initialized",
            "ready": False
        })
    
    try:
        current_url = driver.current_url
        title = driver.title
        
        return jsonify({
            "browser": "ready",
            "ready": True,
            "current_url": current_url,
            "page_title": title
        })
    except Exception as e:
        return jsonify({
            "browser": "error",
            "ready": False,
            "error": str(e)
        })


@app.route('/navigate', methods=['POST'])
def navigate():
    """
    ניווט לכתובת URL
    
    Body:
        {
            "url": "https://example.com"
        }
    """
    global driver
    
    if driver is None:
        driver = init_browser()
    
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        logger.info(f"Navigating to: {url}")
        driver.get(url)
        time.sleep(3)  # המתן לטעינה
        
        return jsonify({
            "success": True,
            "url": driver.current_url,
            "title": driver.title
        })
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/screenshot', methods=['GET'])
def screenshot():
    """
    צילום מסך של הדף הנוכחי
    
    Returns:
        PNG image (base64 encoded in JSON)
    """
    global driver
    
    if driver is None:
        return jsonify({"error": "Browser not initialized"}), 400
    
    try:
        # צלם מסך
        screenshot_png = driver.get_screenshot_as_png()
        
        # המר ל-base64
        screenshot_b64 = base64.b64encode(screenshot_png).decode('utf-8')
        
        return jsonify({
            "success": True,
            "screenshot": screenshot_b64,
            "url": driver.current_url,
            "format": "png"
        })
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/extract_fields', methods=['GET'])
def extract_fields():
    """
    חילוץ כל שדות הטופס מהדף הנוכחי
    """
    global driver
    
    if driver is None:
        return jsonify({"error": "Browser not initialized"}), 400
    
    try:
        # JavaScript לחילוץ שדות
        script = """
        const fields = [];
        const inputs = document.querySelectorAll('input, select, textarea, button');
        
        inputs.forEach((element, index) => {
            const field = {
                index: index,
                tag: element.tagName.toLowerCase(),
                type: element.type || 'text',
                name: element.name || '',
                id: element.id || '',
                placeholder: element.placeholder || '',
                value: element.value || '',
                label: '',
                visible: element.offsetParent !== null,
                required: element.required || false
            };
            
            // חפש label
            if (element.id) {
                const label = document.querySelector(`label[for="${element.id}"]`);
                if (label) field.label = label.textContent.trim();
            }
            
            if (!field.label) {
                const parentLabel = element.closest('label');
                if (parentLabel) field.label = parentLabel.textContent.trim();
            }
            
            fields.push(field);
        });
        
        return fields;
        """
        
        fields = driver.execute_script(script)
        
        # סנן רק שדות נראים
        visible_fields = [f for f in fields if f['visible']]
        
        return jsonify({
            "success": True,
            "fields": visible_fields,
            "total": len(fields),
            "visible": len(visible_fields)
        })
    except Exception as e:
        logger.error(f"Extract fields error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/fill_field', methods=['POST'])
def fill_field():
    """
    מילוי שדה טופס
    
    Body:
        {
            "selector": "#username",  // CSS selector או ID או name
            "value": "myusername",
            "method": "id|name|css"  // אופציונלי
        }
    """
    global driver
    
    if driver is None:
        return jsonify({"error": "Browser not initialized"}), 400
    
    data = request.json
    selector = data.get('selector')
    value = data.get('value')
    method = data.get('method', 'css')  # ברירת מחדל: CSS selector
    
    if not selector or value is None:
        return jsonify({"error": "selector and value are required"}), 400
    
    try:
        # מצא את האלמנט
        if method == 'id':
            element = driver.find_element(By.ID, selector)
        elif method == 'name':
            element = driver.find_element(By.NAME, selector)
        else:  # css
            element = driver.find_element(By.CSS_SELECTOR, selector)
        
        # נקה ומלא
        element.clear()
        element.send_keys(value)
        
        logger.info(f"Filled field {selector} with value")
        
        return jsonify({
            "success": True,
            "selector": selector,
            "filled": True
        })
    except Exception as e:
        logger.error(f"Fill field error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/click', methods=['POST'])
def click():
    """
    לחיצה על אלמנט
    
    Body:
        {
            "selector": "#submit-button",
            "method": "id|name|css|xpath"
        }
    """
    global driver
    
    if driver is None:
        return jsonify({"error": "Browser not initialized"}), 400
    
    data = request.json
    selector = data.get('selector')
    method = data.get('method', 'css')
    
    if not selector:
        return jsonify({"error": "selector is required"}), 400
    
    try:
        # מצא את האלמנט
        if method == 'id':
            element = driver.find_element(By.ID, selector)
        elif method == 'name':
            element = driver.find_element(By.NAME, selector)
        elif method == 'xpath':
            element = driver.find_element(By.XPATH, selector)
        else:  # css
            element = driver.find_element(By.CSS_SELECTOR, selector)
        
        # לחץ
        element.click()
        time.sleep(2)  # המתן אחרי לחיצה
        
        logger.info(f"Clicked on {selector}")
        
        return jsonify({
            "success": True,
            "selector": selector,
            "clicked": True,
            "current_url": driver.current_url
        })
    except Exception as e:
        logger.error(f"Click error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/get_html', methods=['GET'])
def get_html():
    """
    קבלת HTML של הדף הנוכחי
    """
    global driver
    
    if driver is None:
        return jsonify({"error": "Browser not initialized"}), 400
    
    try:
        html = driver.page_source
        
        return jsonify({
            "success": True,
            "html": html,
            "url": driver.current_url,
            "title": driver.title
        })
    except Exception as e:
        logger.error(f"Get HTML error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/execute_js', methods=['POST'])
def execute_js():
    """
    הרצת JavaScript בדף
    
    Body:
        {
            "script": "return document.title;"
        }
    """
    global driver
    
    if driver is None:
        return jsonify({"error": "Browser not initialized"}), 400
    
    data = request.json
    script = data.get('script')
    
    if not script:
        return jsonify({"error": "script is required"}), 400
    
    try:
        result = driver.execute_script(script)
        
        return jsonify({
            "success": True,
            "result": result
        })
    except Exception as e:
        logger.error(f"Execute JS error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/oracle_login', methods=['POST'])
def oracle_login():
    """
    התחברות אוטומטית ל-Oracle Cloud
    
    Body:
        {
            "username": "email@example.com",
            "password": "password123",
            "domain": "Default"
        }
    """
    global driver
    
    if driver is None:
        driver = init_browser()
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    domain = data.get('domain', 'Default')
    
    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400
    
    try:
        # נווט לדף Oracle
        oracle_url = "https://idcs-86c9de635d0e4016b64bfef436100f1e.identity.oraclecloud.com/ui/v1/signin"
        logger.info(f"Navigating to Oracle: {oracle_url}")
        driver.get(oracle_url)
        time.sleep(5)
        
        # מלא username
        try:
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"], input[type="email"], input[name*="user"], input[id*="user"]'))
            )
            username_field.clear()
            username_field.send_keys(username)
            logger.info("✅ Username filled")
        except Exception as e:
            logger.warning(f"Username field not found: {e}")
        
        # מלא password
        try:
            password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_field.clear()
            password_field.send_keys(password)
            logger.info("✅ Password filled")
        except Exception as e:
            logger.warning(f"Password field not found: {e}")
        
        # לחץ Sign In
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
            submit_button.click()
            logger.info("✅ Clicked Sign In")
            time.sleep(5)
        except Exception as e:
            logger.warning(f"Submit button not found: {e}")
        
        # צלם מסך
        screenshot_png = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot_png).decode('utf-8')
        
        return jsonify({
            "success": True,
            "current_url": driver.current_url,
            "page_title": driver.title,
            "screenshot": screenshot_b64
        })
    except Exception as e:
        logger.error(f"Oracle login error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # אתחל דפדפן בהתחלה
    init_browser()
    
    # הרץ Flask server
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
