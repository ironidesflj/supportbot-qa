import urllib.request, json
req = urllib.request.Request("https://api.browser-use.com/cloud/signup", data=b'{}', method="POST", headers={"Content-Type": "application/json"})
res = json.loads(urllib.request.urlopen(req).read())
print(json.dumps(res))
