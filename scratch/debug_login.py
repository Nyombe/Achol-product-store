import requests
import sys

url = "https://achol-fashion-store.onrender.com/auth/login/"
s = requests.Session()

try:
    print("Fetching CSRF token...")
    r = s.get(url)
    csrf_token = s.cookies.get('csrftoken')
    if not csrf_token:
        # Check if it's in the HTML
        from html.parser import HTMLParser
        class CSRFParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.token = None
            def handle_starttag(self, tag, attrs):
                if tag == 'input':
                    attrs_dict = dict(attrs)
                    if attrs_dict.get('name') == 'csrfmiddlewaretoken':
                        self.token = attrs_dict.get('value')
        
        parser = CSRFParser()
        parser.feed(r.text)
        csrf_token = parser.token

    print(f"CSRF Token found: {csrf_token}")

    data = {
        'username': 'testuser',
        'password': 'testpassword',
        'csrfmiddlewaretoken': csrf_token
    }

    print("Sending POST request to login...")
    r = s.post(url, data=data, headers={'Referer': url})
    print(f"Status Code: {r.status_code}")
    
    if r.status_code == 500 or 'Traceback' in r.text:
        print("--- START ERROR CONTENT ---")
        print(r.text[:5000])
        print("--- END ERROR CONTENT ---")
    else:
        print("No 500 error detected in POST response.")
        print(r.text[:500])

except Exception as e:
    print(f"Error occurred during request: {e}")
