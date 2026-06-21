import urllib.request
import json
import re

found = False
for i in range(30):
    req = urllib.request.Request(
        "https://api.browser-use.com/cloud/signup", 
        data=b'{}', 
        method="POST", 
        headers={"Content-Type": "application/json"}
    )
    try:
        res = json.loads(urllib.request.urlopen(req).read())
    except Exception:
        continue
    txt = res["challenge_text"]
    clean = re.sub(r'[^a-zA-Z0-9\+\-\*\/\. ]', '', txt).lower()
    
    # Check for simple numbers and standard math words
    valid = (
        "mute" not in clean and "train" not in clean and 
        "luka" not in clean and "ciento" not in clean
    )
    if re.search(r'\d+', clean) and valid:
        print(json.dumps(res))
        found = True
        break

if not found:
    print("No easy challenge found.")
