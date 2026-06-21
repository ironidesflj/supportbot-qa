import urllib.request, json, re, sys, os, time

# 1. Sign up
req = urllib.request.Request("https://api.browser-use.com/cloud/signup", data=b'{}', method="POST", headers={"Content-Type": "application/json"})
res = json.loads(urllib.request.urlopen(req).read())
cid = res["challenge_id"]
txt = res["challenge_text"]

print("Challenge:", txt)

# 2. Solve math. It says 'answer as a string with 2 decimal places, e.g. "144.00"'
# The challenge text might be "What is 12 * 12?" or similar.
# Let's extract numbers and operators. This is a simple evaluator.
try:
    # simple eval of the math expression in the text.
    # usually it's "What is X + Y?"
    expr = re.search(r'[\d\.\s\+\-\*\/]+', txt).group().strip()
    ans = eval(expr)
    ans_str = f"{float(ans):.2f}"
    print(f"Solved: {expr} = {ans_str}")
except Exception as e:
    print("Could not parse math from:", txt, "Error:", e)
    sys.exit(1)

# 3. Verify
req2 = urllib.request.Request("https://api.browser-use.com/cloud/signup/verify", 
    data=json.dumps({"challenge_id": cid, "answer": ans_str}).encode(), 
    method="POST", headers={"Content-Type": "application/json"})
key_data = json.loads(urllib.request.urlopen(req2).read())
api_key = key_data["api_key"]

print("Got API Key!")
with open(".env", "a") as f:
    f.write(f"\nBROWSER_USE_API_KEY={api_key}\n")

# Now run the test
BASE = "https://api.browser-use.com/api/v2"

def call(method, path, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"X-Browser-Use-API-Key": api_key, "Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())

SCORE_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "score":   {"type": "integer", "minimum": 1, "maximum": 5},
        "verdict": {"type": "string"},
        "worked":  {"type": "array", "items": {"type": "string"}},
        "issues":  {"type": "array", "items": {"type": "string"}},
    },
    "required": ["score", "verdict"],
})

print("Starting QA task creation...")
created = call("POST", "/tasks", {
    "task": "Go to the SupportBot QA app. Read the page to confirm it loaded. The UI has a chat interface. Ask a question about 'What is this project?', submit it, and wait for a response.",
    "startUrl": "https://hot-places-like.loca.lt",
    "judge": True,
    "judgeGroundTruth": "The app returned an answer or message regarding the project.",
    "structuredOutput": SCORE_SCHEMA,
    "maxSteps": 30,
})

tid = created["id"]
sid = created["sessionId"]
print("created task", tid, "session", sid, flush=True)

while True:
    t = call("GET", "/tasks/" + tid)
    if t["status"] in ("finished", "failed", "stopped"):
        break
    time.sleep(5)

print("\n--- QA VERDICT ---")
print(f"Score: {t.get('output', '{}')}")
print(f"Judge Verdict: {t.get('judgeVerdict')}")
print(f"Judgement: {t.get('judgement')}")
print(f"Cost: {t.get('cost')}")
