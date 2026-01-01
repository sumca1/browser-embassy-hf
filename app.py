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


@app.route('/create_anthropic_key', methods=['POST'])
def create_anthropic_key():
    """
    🔑 יצירת API Key אוטומטית ב-Anthropic Console
    
    תהליך אוטומטי מלא:
    1. וודא שהדפדפן ב-Anthropic Console
    2. לחץ על "Create Key"
    3. מלא שם (אופציונלי)
    4. לחץ "Create"
    5. חלץ את ה-Key
    6. החזר את ה-Key
    
    Body (אופציונלי):
        {
            "key_name": "My API Key"  // אופציונלי, ברירת מחדל: "Auto-generated Key"
        }
    
    Returns:
        {
            "success": true,
            "api_key": "sk-ant-api03-...",
            "key_name": "My API Key"
        }
    """
    global driver
    
    if driver is None:
        driver = init_browser()
    
    data = request.json or {}
    key_name = data.get('key_name', f'Auto-generated Key {time.strftime("%Y%m%d_%H%M%S")}')
    
    try:
        logger.info("🔑 Starting Anthropic Key creation automation...")
        
        # וודא שאנחנו בדף הנכון
        current_url = driver.current_url
        if 'console.anthropic.com' not in current_url:
            logger.info("Navigating to Anthropic Console...")
            driver.get('https://console.anthropic.com/settings/keys')
            time.sleep(5)
        
        # צלם מסך התחלתי
        logger.info("📸 Taking initial screenshot...")
        screenshot_before = driver.get_screenshot_as_png()
        screenshot_before_b64 = base64.b64encode(screenshot_before).decode('utf-8')
        
        # חפש כפתור "Create Key" או דומה
        logger.info("🔍 Looking for 'Create Key' button...")
        
        # ניסיונות שונים למצוא את הכפתור
        button_selectors = [
            'button:has-text("Create Key")',
            'button:has-text("New Key")',
            'button[aria-label*="Create"]',
            'button[aria-label*="New"]',
            'a:has-text("Create Key")',
            'button.create-key',
            'button[data-test="create-key"]',
            # Fallback: כל כפתור שמכיל "create" או "key"
            '//button[contains(translate(text(), "CREATE", "create"), "create")]',
            '//button[contains(translate(text(), "KEY", "key"), "key")]',
        ]
        
        create_button = None
        for selector in button_selectors:
            try:
                if selector.startswith('//'):
                    # XPath
                    create_button = driver.find_element(By.XPATH, selector)
                else:
                    # CSS
                    create_button = driver.find_element(By.CSS_SELECTOR, selector)
                
                if create_button:
                    logger.info(f"✅ Found button with selector: {selector}")
                    break
            except:
                continue
        
        if not create_button:
            # אם לא מצאנו, נסה JavaScript
            logger.info("Trying JavaScript fallback...")
            script = """
            const buttons = Array.from(document.querySelectorAll('button, a'));
            const createBtn = buttons.find(btn => 
                btn.textContent.toLowerCase().includes('create') &&
                (btn.textContent.toLowerCase().includes('key') || btn.textContent.toLowerCase().includes('api'))
            );
            if (createBtn) {
                createBtn.scrollIntoView();
                return true;
            }
            return false;
            """
            found = driver.execute_script(script)
            if found:
                logger.info("✅ Found button via JavaScript")
            else:
                # אם עדיין לא מצאנו - החזר screenshot וטקסט הדף
                logger.warning("⚠️ Could not find Create Key button")
                page_text = driver.execute_script("return document.body.innerText;")
                
                return jsonify({
                    "success": False,
                    "error": "Could not find 'Create Key' button",
                    "page_text_preview": page_text[:500],
                    "screenshot": screenshot_before_b64,
                    "current_url": driver.current_url,
                    "suggestion": "Please check if you need to login first or if the page structure changed"
                }), 404
        
        # לחץ על הכפתור
        logger.info("🖱️ Clicking 'Create Key' button...")
        if create_button:
            create_button.click()
        else:
            # JavaScript click
            driver.execute_script("""
                const buttons = Array.from(document.querySelectorAll('button, a'));
                const createBtn = buttons.find(btn => 
                    btn.textContent.toLowerCase().includes('create') &&
                    (btn.textContent.toLowerCase().includes('key') || btn.textContent.toLowerCase().includes('api'))
                );
                if (createBtn) createBtn.click();
            """)
        
        time.sleep(3)
        
        # חפש שדה שם (אם קיים)
        logger.info("🔍 Looking for name field...")
        try:
            name_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"], input[placeholder*="name" i], input[name*="name" i]'))
            )
            name_field.clear()
            name_field.send_keys(key_name)
            logger.info(f"✅ Filled key name: {key_name}")
            time.sleep(1)
        except Exception as e:
            logger.info(f"No name field found (might not be required): {e}")
        
        # חפש כפתור אישור (Create/Confirm/Submit)
        logger.info("🔍 Looking for confirmation button...")
        confirm_selectors = [
            'button:has-text("Create")',
            'button:has-text("Confirm")',
            'button:has-text("Submit")',
            'button[type="submit"]',
            'button.primary',
            '//button[contains(translate(text(), "CREATE", "create"), "create")]',
            '//button[contains(translate(text(), "CONFIRM", "confirm"), "confirm")]',
        ]
        
        confirm_button = None
        for selector in confirm_selectors:
            try:
                if selector.startswith('//'):
                    confirm_button = driver.find_element(By.XPATH, selector)
                else:
                    confirm_button = driver.find_element(By.CSS_SELECTOR, selector)
                
                if confirm_button and confirm_button != create_button:  # וודא שזה לא אותו כפתור
                    logger.info(f"✅ Found confirm button: {selector}")
                    break
            except:
                continue
        
        if confirm_button:
            confirm_button.click()
            logger.info("✅ Clicked confirmation button")
        else:
            # JavaScript fallback
            driver.execute_script("""
                const buttons = Array.from(document.querySelectorAll('button'));
                const confirmBtn = buttons.find(btn => 
                    (btn.textContent.toLowerCase().includes('create') ||
                     btn.textContent.toLowerCase().includes('confirm') ||
                     btn.type === 'submit') &&
                    btn.offsetParent !== null  // visible
                );
                if (confirmBtn) confirmBtn.click();
            """)
        
        time.sleep(3)
        
        # חפש את ה-Key שנוצר
        logger.info("🔍 Extracting API Key...")
        
        # JavaScript לחיפוש Key (מחפש מחרוזת שמתחילה ב-sk-ant-)
        extract_script = """
        // חפש בכל הטקסטים בדף
        const allText = document.body.innerText;
        const keyMatch = allText.match(/sk-ant-[a-zA-Z0-9_-]{95,}/);
        if (keyMatch) return keyMatch[0];
        
        // חפש בשדות input/textarea
        const inputs = document.querySelectorAll('input[type="text"], input[readonly], textarea[readonly], code, pre');
        for (const input of inputs) {
            const value = input.value || input.textContent || input.innerText;
            if (value && value.startsWith('sk-ant-')) {
                return value.trim();
            }
        }
        
        // חפש elements עם data attributes
        const elements = document.querySelectorAll('[data-key], [data-api-key], [data-value]');
        for (const el of elements) {
            for (const attr of el.attributes) {
                if (attr.value && attr.value.startsWith('sk-ant-')) {
                    return attr.value.trim();
                }
            }
        }
        
        return null;
        """
        
        api_key = driver.execute_script(extract_script)
        
        # צלם מסך סופי
        screenshot_after = driver.get_screenshot_as_png()
        screenshot_after_b64 = base64.b64encode(screenshot_after).decode('utf-8')
        
        if api_key:
            logger.info(f"✅ Successfully extracted API Key: {api_key[:20]}...")
            
            return jsonify({
                "success": True,
                "api_key": api_key,
                "key_name": key_name,
                "screenshot_before": screenshot_before_b64,
                "screenshot_after": screenshot_after_b64,
                "current_url": driver.current_url
            })
        else:
            # אם לא הצלחנו לחלץ - החזר מידע לבאג דיבוג
            logger.warning("⚠️ Could not extract API Key")
            page_html = driver.page_source
            
            return jsonify({
                "success": False,
                "error": "Could not extract API Key from page",
                "screenshot": screenshot_after_b64,
                "current_url": driver.current_url,
                "page_html_length": len(page_html),
                "suggestion": "Check screenshot to see if key was created. Might need manual extraction."
            }), 404
    
    except Exception as e:
        logger.error(f"❌ Anthropic Key creation error: {e}")
        
        # צלם מסך של השגיאה
        try:
            screenshot_error = driver.get_screenshot_as_png()
            screenshot_error_b64 = base64.b64encode(screenshot_error).decode('utf-8')
        except:
            screenshot_error_b64 = None
        
        return jsonify({
            "error": str(e),
            "screenshot": screenshot_error_b64,
            "current_url": driver.current_url if driver else None
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """
    בדיקת בריאות ה-API
    """
    global driver
    
    return jsonify({
        "status": "healthy",
        "browser_initialized": driver is not None,
        "browser_ready": driver is not None,
        "current_url": driver.current_url if driver else None,
        "timestamp": time.time()
    })


if __name__ == '__main__':
    # אתחל דפדפן בהתחלה
    init_browser()
    
    # הרץ Flask server
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
