"""QA automation runner using the Browser-Use cloud API.

Environment variables (read from .env):
    BROWSER_USE_API_KEY: Your Browser-Use cloud API key (required).
    QA_START_URL: Public URL of the app to test (required).
    QA_TASK (optional): Custom task description for the QA agent.
    QA_GROUND_TRUTH (optional): Custom ground truth for the judge.

Usage:
    python3 run_qa.py
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE = "https://api.browser-use.com/api/v2"


def get_env_or_die(key: str) -> str:
    """Reads an env var or exits with an error message."""
    val = os.environ.get(key, "").strip()
    if not val:
        print(f"ERROR: environment variable '{key}' is not set.")
        print("Hint: add it to your .env file (see .env.example).")
        sys.exit(1)
    return val


def call(method: str, path: str, api_key: str, body=None):
    """Call the Browser-Use API."""
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={
            "X-Browser-Use-API-Key": api_key,
            "Content-Type": "application/json",
        },
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


def main():
    """Create and poll a Browser-Use QA task, then print the verdict."""
    api_key = get_env_or_die("BROWSER_USE_API_KEY")
    start_url = get_env_or_die("QA_START_URL")

    task_desc = os.environ.get(
        "QA_TASK",
        "Acesse a URL e clique em 'Click to Continue' se houver aviso de tunnel. "
        "Na aplicacao SupportBot QA, mande a pergunta 'What is this project?' "
        "no chat, aguarde a resposta aparecer na tela e analise a qualidade.",
    )
    ground_truth = os.environ.get(
        "QA_GROUND_TRUTH",
        "O bot de chat retornou uma resposta para a pergunta.",
    )

    print("Iniciando a tarefa de QA...")
    print(f"  Start URL: {start_url}")
    print()

    created = call("POST", "/tasks", api_key, {
        "task": task_desc,
        "startUrl": start_url,
        "judge": True,
        "judgeGroundTruth": ground_truth,
        "structuredOutput": SCORE_SCHEMA,
        "maxSteps": 30,
    })

    tid = created["id"]
    sid = created["sessionId"]
    watch_url = f"https://cloud.browser-use.com/thread/{sid}"
    print(f"Tarefa Criada! ID: {tid}")
    print(f"Acompanhe o agente ao vivo: {watch_url}\n")

    while True:
        t = call("GET", "/tasks/" + tid, api_key)
        if t["status"] in ("finished", "failed", "stopped"):
            break
        time.sleep(5)
        print(".", end="", flush=True)

    print("\n\n--- RESULTADO DO QA ---")
    out = t.get("output", "{}")
    if isinstance(out, str):
        try:
            out = json.loads(out)
        except Exception:
            out = {"verdict": out}

    score = out.get("score", "N/A")
    print(f"Score: {score}/5")
    print(f"Resultado: {'PASSOU' if t.get('judgeVerdict') else 'FALHOU'}")
    print("O que funcionou:")
    for item in out.get("worked", []):
        print(f"  - {item}")
    print("Problemas:")
    for item in out.get("issues", []):
        print(f"  - {item}")
    print(f"Detalhe do Juiz: {t.get('judgement')}")
    print(f"Custo: ${t.get('cost')} ({len(t.get('steps', []))} passos)")


if __name__ == "__main__":
    main()
