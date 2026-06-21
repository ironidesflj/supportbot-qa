import urllib.request, json, sys, time

KEY = "REDACTED_BROWSERUSE_KEY"
BASE = "https://api.browser-use.com/api/v2"

def call(method, path, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"X-Browser-Use-API-Key": KEY, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code} - {e.read().decode()[:500]}")
        sys.exit(1)

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

print("Iniciando a tarefa de QA...")
created = call("POST", "/tasks", {
    "task": "Acesse a URL e clique em 'Click to Continue' se houver um aviso do localtunnel. Na aplicação SupportBot QA, mande a pergunta 'What is this project?' no chat, aguarde a resposta aparecer na tela, e analise a qualidade da resposta.",
    "startUrl": "https://small-boxes-matter.loca.lt",
    "judge": True,
    "judgeGroundTruth": "O bot de chat retornou uma resposta para a pergunta.",
    "structuredOutput": SCORE_SCHEMA,
    "maxSteps": 30,
})

tid = created["id"]
sid = created["sessionId"]
watch_url = f"https://cloud.browser-use.com/thread/{sid}"
print(f"\nTarefa Criada! ID: {tid}")
print(f"Acompanhe o agente ao vivo pelo navegador: {watch_url}\n")

import subprocess
cmds = [["open", "-a", "Google Chrome", watch_url], ["open", watch_url]]
for c in cmds:
    try:
        subprocess.Popen(c, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        break
    except Exception:
        continue

while True:
    t = call("GET", "/tasks/" + tid)
    if t["status"] in ("finished", "failed", "stopped"):
        break
    time.sleep(5)
    print(".", end="", flush=True)

print("\n\n--- RESULTADO DO QA ---")
out = t.get("output", "{}")
if isinstance(out, str):
    try:
        out = json.loads(out)
    except:
        out = {"verdict": out}

score = out.get('score', 'N/A')
print(f"Score: {score}/5")
print(f"Resultado: {'PASSOU' if t.get('judgeVerdict') else 'FALHOU'}")
print(f"O que funcionou:\n" + "\n".join(f"- {i}" for i in out.get("worked", [])))
print(f"Problemas:\n" + "\n".join(f"- {i}" for i in out.get("issues", [])))
print(f"Detalhe do Juiz: {t.get('judgement')}")
print(f"Custo: ${t.get('cost')} ({len(t.get('steps', []))} passos)")
