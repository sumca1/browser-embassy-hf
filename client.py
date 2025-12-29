"""
🎮 Browser Embassy Client - שליטה מרחוק בדפדפן
=================================================

Client לשליטה בדפדפן על HuggingFace Spaces
"""

import requests
import base64
import json
from pathlib import Path
from PIL import Image
from io import BytesIO
import time

class BrowserEmbassyClient:
    """
    Client לשליטה בדפדפן מרחוק
    """
    
    def __init__(self, base_url="https://kuperberg-browser-embassy.hf.space"):
        """
        אתחול Client
        
        Args:
            base_url: כתובת ה-Space ב-HuggingFace
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def status(self):
        """
        בדיקת סטטוס הדפדפן
        """
        response = self.session.get(f'{self.base_url}/status')
        return response.json()
    
    def navigate(self, url):
        """
        ניווט לכתובת
        """
        response = self.session.post(
            f'{self.base_url}/navigate',
            json={'url': url}
        )
        return response.json()
    
    def screenshot(self, save_path=None):
        """
        צילום מסך
        
        Args:
            save_path: נתיב לשמירת הקובץ (אופציונלי)
        
        Returns:
            PIL Image object
        """
        response = self.session.get(f'{self.base_url}/screenshot')
        data = response.json()
        
        if not data.get('success'):
            raise Exception(f"Screenshot failed: {data.get('error')}")
        
        # המר מ-base64 לתמונה
        img_data = base64.b64decode(data['screenshot'])
        img = Image.open(BytesIO(img_data))
        
        # שמור אם נדרש
        if save_path:
            img.save(save_path)
            print(f"📸 Screenshot saved to: {save_path}")
        
        return img
    
    def extract_fields(self):
        """
        חילוץ שדות טופס
        """
        response = self.session.get(f'{self.base_url}/extract_fields')
        return response.json()
    
    def fill_field(self, selector, value, method='css'):
        """
        מילוי שדה
        
        Args:
            selector: CSS selector, ID, or name
            value: הערך למילוי
            method: 'css', 'id', or 'name'
        """
        response = self.session.post(
            f'{self.base_url}/fill_field',
            json={
                'selector': selector,
                'value': value,
                'method': method
            }
        )
        return response.json()
    
    def click(self, selector, method='css'):
        """
        לחיצה על אלמנט
        
        Args:
            selector: CSS selector, ID, name, or XPath
            method: 'css', 'id', 'name', or 'xpath'
        """
        response = self.session.post(
            f'{self.base_url}/click',
            json={
                'selector': selector,
                'method': method
            }
        )
        return response.json()
    
    def get_html(self):
        """
        קבלת HTML של הדף
        """
        response = self.session.get(f'{self.base_url}/get_html')
        return response.json()
    
    def execute_js(self, script):
        """
        הרצת JavaScript
        
        Args:
            script: קוד JavaScript להרצה
        """
        response = self.session.post(
            f'{self.base_url}/execute_js',
            json={'script': script}
        )
        return response.json()
    
    def oracle_login(self, username, password, domain='Default'):
        """
        התחברות אוטומטית ל-Oracle Cloud
        
        Args:
            username: שם משתמש (email)
            password: סיסמה
            domain: דומיין (ברירת מחדל: Default)
        """
        print(f"🔐 Logging into Oracle Cloud...")
        print(f"   Username: {username}")
        print(f"   Domain: {domain}")
        
        response = self.session.post(
            f'{self.base_url}/oracle_login',
            json={
                'username': username,
                'password': password,
                'domain': domain
            }
        )
        
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Login process completed")
            print(f"📍 Current URL: {result.get('current_url')}")
            print(f"📄 Page title: {result.get('page_title')}")
            
            # שמור screenshot
            if result.get('screenshot'):
                img_data = base64.b64decode(result['screenshot'])
                img = Image.open(BytesIO(img_data))
                img.save('oracle_login_result.png')
                print(f"📸 Screenshot saved: oracle_login_result.png")
        
        return result


def test_oracle_embassy():
    """
    בדיקה של התחברות ל-Oracle דרך Embassy
    """
    print("""
╔═══════════════════════════════════════════════════════════════╗
║        🌐 Browser Embassy - Oracle Cloud Login Test          ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # יצירת client
    client = BrowserEmbassyClient()
    
    # בדוק סטטוס
    print("🔍 Checking browser status...")
    status = client.status()
    print(f"   Browser: {status.get('browser')}")
    print(f"   Ready: {status.get('ready')}")
    
    # התחבר ל-Oracle
    result = client.oracle_login(
        username='s8001145@gmail.com',
        password='WnC6PgyLXGxDN4A!',
        domain='Default'
    )
    
    if result.get('success'):
        print("\n🎉 Embassy is working! Browser is running on HuggingFace!")
        print("🔓 No NetFree blocking - we're in the cloud!")
    else:
        print(f"\n❌ Error: {result.get('error')}")


if __name__ == "__main__":
    test_oracle_embassy()
