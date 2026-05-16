# rkitect.ai — Daily Content Automation Pipeline v2

## End-to-End Build Guide · HappyMonk AI · May 2026

> \*\*Stack:\*\* Python 3.11+ · Anthropic SDK · OpenAI SDK (for OpenRouter) · Buffer API · Flask Dashboard · Cron  
> \*\*Platforms:\*\* Twitter/X · Instagram · LinkedIn · Reddit (placeholder — confirm tool)  
> \*\*Models:\*\* Task-routed across Claude, OpenRouter (Gemini, Mistral, GPT-4o-mini, Llama)

\---

## 1\. What's New in v2

| Feature               | Detail                                                                               |
| --------------------- | ------------------------------------------------------------------------------------ |
| Dual API support      | Claude API + OpenRouter — assign any model to any task                               |
| Model routing         | Different model per task: cheap fast models for research, premium for writing and QA |
| Dashboard             | Flask web UI showing today's topics, generated content, QA scores, Buffer schedule   |
| Self-improving skills | Meta-agent rewrites underperforming prompts after every 7 runs                       |
| Reddit posting        | Placeholder — wire once Reddit tool confirmed                                        |

\---

## 2\. Updated Folder Structure

```
rkitect-pipeline/
│
├── main.py                        # Orchestrator
├── config.py                      # All settings, model assignments, API keys
├── model\_router.py                # Central model routing — picks provider + model per task
├── requirements.txt
│
├── agents/
│   ├── research.py
│   ├── filter.py
│   ├── generate.py
│   ├── qa.py
│   ├── publish.py
│   └── self\_improve.py            # NEW — rewrites prompts based on performance
│
├── prompts/
│   ├── research\_agent.md
│   ├── filter\_agent.md
│   ├── linkedin\_writer.md
│   ├── carousel\_writer.md
│   ├── reel\_writer.md
│   ├── twitter\_writer.md
│   ├── reddit\_writer.md           # PLACEHOLDER
│   └── qa\_reviewer.md
│
├── prompts/versions/              # NEW — archived prompt versions
│   └── linkedin\_writer\_v1\_2026-05-14.md
│
├── context/
│   ├── brand\_bible.md
│   ├── voice\_rules.md
│   ├── competitor\_watch.md
│   ├── content\_pillars.md
│   └── skill\_performance.json     # NEW — running QA score history per format
│
├── dashboard/
│   ├── app.py                     # Flask server
│   ├── templates/
│   │   └── index.html             # Single-page dashboard
│   └── static/
│       └── style.css
│
├── logs/
│   └── YYYY-MM-DD.json
│
└── output/
    └── YYYY-MM-DD/
        ├── topics.json
        ├── linkedin\_post.md
        ├── carousel.md
        ├── reel\_script.md
        ├── twitter\_thread.md
        └── reddit\_post.md
```

\---

## 3\. Environment Variables

```env
# ── Anthropic (Claude) ──────────────────────────────
ANTHROPIC\_API\_KEY=sk-ant-...

# ── OpenRouter ──────────────────────────────────────
OPENROUTER\_API\_KEY=sk-or-...

# ── Buffer ──────────────────────────────────────────
BUFFER\_ACCESS\_TOKEN=...
BUFFER\_INSTAGRAM\_PROFILE\_ID=...
BUFFER\_LINKEDIN\_PROFILE\_ID=...
BUFFER\_TWITTER\_PROFILE\_ID=...
# BUFFER\_REDDIT\_PROFILE\_ID=...     # Add once confirmed

# ── Dashboard ───────────────────────────────────────
DASHBOARD\_PORT=5050
DASHBOARD\_SECRET\_KEY=change-me-to-something-random

# ── Optional: Slack run notifications ───────────────
SLACK\_WEBHOOK\_URL=
```

\---

## 4\. config.py

```python
import os
from dotenv import load\_dotenv

load\_dotenv()

# ── API Keys ────────────────────────────────────────────────────────────────
ANTHROPIC\_API\_KEY    = os.getenv("ANTHROPIC\_API\_KEY")
OPENROUTER\_API\_KEY   = os.getenv("OPENROUTER\_API\_KEY")

# ── Model Routing ────────────────────────────────────────────────────────────
# Format: {"provider": "claude" | "openrouter", "model": "model-string"}
# Claude models:     claude-sonnet-4-20250514 | claude-haiku-4-5-20251001
# OpenRouter models: google/gemini-flash-1.5 | mistralai/mistral-7b-instruct
#                    openai/gpt-4o-mini | meta-llama/llama-3.1-8b-instruct
#                    anthropic/claude-sonnet-4-5 (Claude via OpenRouter — slightly pricier)

MODEL\_ROUTING = {
    # Research — needs web search, speed > quality. Gemini Flash is cheap + fast.
    "research":     {"provider": "openrouter", "model": "google/gemini-2.0-flash-001"},

    # Filter — lightweight reasoning. Mistral 7B is accurate and nearly free.
    "filter":       {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct-v0.1"},

    # LinkedIn — highest quality writing. Use Claude directly.
    "linkedin":     {"provider": "claude",     "model": "moonshotai/kimi-k2.5"},
    # "linkedin":     {"provider": "claude",     "model": "claude-sonnet-4-20250514"},

    # Carousel — good creative output. GPT-4o-mini is cheap and competent.
    "carousel":     {"provider": "openrouter", "model": "openai/gpt-4o-mini"},

    # Reel — scripting, punchy. GPT-4o-mini works well here.
    "reel":         {"provider": "openrouter", "model": "openai/gpt-4o-mini"},

    # Twitter — short, sharp. Mistral handles this fine.
    "twitter":      {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct-v0.1"},

    # Reddit — placeholder until posting tool confirmed
    "reddit":       {"provider": "openrouter", "model": "openai/gpt-4o-mini"},

    # QA — brand rule enforcement needs precision. Claude only.
    "qa":           {"provider": "claude",     "model": "moonshotai/kimi-k2.5"},

    # Self-improve — meta-reasoning on prompts. Claude only.
    "self\_improve": {"provider": "claude",     "model": "moonshotai/kimi-k2.5"},
}

# ── Buffer ───────────────────────────────────────────────────────────────────
BUFFER\_ACCESS\_TOKEN = os.getenv("BUFFER\_ACCESS\_TOKEN")
BUFFER\_PROFILES = {
    "instagram": os.getenv("BUFFER\_INSTAGRAM\_PROFILE\_ID"),
    "linkedin":  os.getenv("BUFFER\_LINKEDIN\_PROFILE\_ID"),
    "twitter":   os.getenv("BUFFER\_TWITTER\_PROFILE\_ID"),
    # "reddit":  os.getenv("BUFFER\_REDDIT\_PROFILE\_ID"),
}

# ── Content Pillars ──────────────────────────────────────────────────────────
CONTENT\_PILLARS = {
    "education\_insight":            0.35,
    "social\_proof\_transformation":  0.25,
    "inspiration\_trend":            0.20,
    "behind\_the\_product":           0.10,
    "cta\_conversion":               0.10,
}

# ── QA Settings ──────────────────────────────────────────────────────────────
QA\_PASS\_THRESHOLD      = 80
QA\_MAX\_RETRIES         = 3

# ── Self-Improvement ─────────────────────────────────────────────────────────
SELF\_IMPROVE\_EVERY\_N\_RUNS = 7    # Rewrite underperforming prompts every 7 runs
SELF\_IMPROVE\_THRESHOLD    = 75   # Rewrite prompt if average score is below this

# ── Paths ────────────────────────────────────────────────────────────────────
PROMPTS\_DIR    = "prompts"
CONTEXT\_DIR    = "context"
OUTPUT\_DIR     = "output"
LOGS\_DIR       = "logs"
VERSIONS\_DIR   = "prompts/versions"
PERF\_LOG       = "context/skill\_performance.json"

# ── Dashboard ────────────────────────────────────────────────────────────────
DASHBOARD\_PORT       = int(os.getenv("DASHBOARD\_PORT", 5050))
DASHBOARD\_SECRET\_KEY = os.getenv("DASHBOARD\_SECRET\_KEY", "dev-secret")
```

\---

## 5\. model_router.py

Single source of truth for all LLM calls. Every agent goes through here.

```python
import anthropic
from openai import OpenAI
from config import (
    ANTHROPIC\_API\_KEY, OPENROUTER\_API\_KEY, MODEL\_ROUTING
)

\_anthropic\_client = anthropic.Anthropic(api\_key=ANTHROPIC\_API\_KEY)

\_openrouter\_client = OpenAI(
    base\_url="https://openrouter.ai/api/v1",
    api\_key=OPENROUTER\_API\_KEY,
    default\_headers={
        "HTTP-Referer": "https://rkitect.ai",
        "X-Title": "rkitect-content-pipeline",
    }
)

def call\_model(
    task: str,
    system: str,
    user: str,
    max\_tokens: int = 2000,
    use\_web\_search: bool = False,
) -> str:
    """
    Route a call to the correct provider + model for the given task.
    Returns the text response as a string.
    """
    config   = MODEL\_ROUTING.get(task, MODEL\_ROUTING\["linkedin"])
    provider = config\["provider"]
    model    = config\["model"]

    if provider == "claude":
        kwargs = dict(
            model=model,
            max\_tokens=max\_tokens,
            system=system,
            messages=\[{"role": "user", "content": user}],
        )
        if use\_web\_search:
            kwargs\["tools"] = \[{"type": "web\_search\_20250305", "name": "web\_search"}]

        response = \_anthropic\_client.messages.create(\*\*kwargs)
        return "".join(b.text for b in response.content if b.type == "text")

    elif provider == "openrouter":
        # OpenRouter uses OpenAI-compatible API
        # Web search: some OR models support it via tool\_choice; default to prompt-based
        messages = \[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ]
        response = \_openrouter\_client.chat.completions.create(
            model=model,
            max\_tokens=max\_tokens,
            messages=messages,
        )
        return response.choices\[0].message.content or ""

    raise ValueError(f"Unknown provider: {provider}")
```

\---

## 6\. agents/research.py

```python
import json, re
from datetime import date
from model\_router import call\_model
from utils.context\_loader import load\_brand\_context, load\_prompt

def run\_research() -> dict:
    system = load\_brand\_context() + "\\n\\n---\\n\\n" + load\_prompt("research\_agent")
    user   = (
        f"Today is {date.today()}. Run your full research sweep. "
        "Return exactly 5 topics as a JSON object."
    )
    # Research uses web search — only works with Claude provider
    # If using OpenRouter for research, web search is prompt-instructed (best effort)
    result = call\_model("research", system, user, max\_tokens=2000, use\_web\_search=True)

    json\_match = re.search(r'\\{.\*\\}', result, re.DOTALL)
    if json\_match:
        return json.loads(json\_match.group())
    return {"topics": \[], "raw": result, "error": "Parse failed"}
```

\---

## 7\. agents/filter.py

```python
import json, re
from model\_router import call\_model
from utils.context\_loader import load\_brand\_context, load\_prompt
from config import CONTENT\_PILLARS

def run\_filter(research: dict) -> dict:
    system = load\_brand\_context() + "\\n\\n---\\n\\n" + load\_prompt("filter\_agent")
    user   = (
        f"Pillar weights:\\n{json.dumps(CONTENT\_PILLARS, indent=2)}\\n\\n"
        f"Topics:\\n{json.dumps(research.get('topics', \[]), indent=2)}\\n\\n"
        "Select the best topic. Return JSON."
    )
    result     = call\_model("filter", system, user, max\_tokens=800)
    json\_match = re.search(r'\\{.\*\\}', result, re.DOTALL)
    if json\_match:
        return json.loads(json\_match.group())
    return {"error": "Filter failed", "raw": result}
```

\---

## 8\. agents/generate.py

```python
import concurrent.futures
from model\_router import call\_model
from utils.context\_loader import load\_brand\_context, load\_prompt

FORMATS = \["linkedin", "carousel", "reel", "twitter", "reddit"]

def \_generate\_one(fmt: str, topic: dict, brand\_context: str) -> tuple\[str, str]:
    system = brand\_context + "\\n\\n---\\n\\n" + load\_prompt(f"{fmt}\_writer")
    critique\_note = ""
    if topic.get("critique"):
        critique\_note = f"\\n\\nPREVIOUS VERSION FAILED QA. Critique to address:\\n{topic\['critique']}"

    user = (
        f"Topic: {topic.get('selected\_topic')}\\n"
        f"Pillar: {topic.get('pillar')}\\n"
        f"Angle: {topic.get('angle')}"
        f"{critique\_note}\\n\\n"
        f"Write the {fmt} content now."
    )
    result = call\_model(fmt, system, user, max\_tokens=2000)
    return fmt, result

def run\_generation(topic: dict) -> dict:
    brand\_context = load\_brand\_context()
    results       = {}

    with concurrent.futures.ThreadPoolExecutor(max\_workers=5) as executor:
        futures = {
            executor.submit(\_generate\_one, fmt, topic, brand\_context): fmt
            for fmt in FORMATS
        }
        for future in concurrent.futures.as\_completed(futures):
            fmt, result = future.result()
            results\[fmt] = result

    return results
```

\---

## 9\. agents/qa.py

```python
import json, re
from model\_router import call\_model
from utils.context\_loader import load\_brand\_context, load\_prompt
from config import QA\_PASS\_THRESHOLD

def score\_content(fmt: str, content: str) -> dict:
    system = load\_brand\_context() + "\\n\\n---\\n\\n" + load\_prompt("qa\_reviewer")
    user   = (
        f"Format: {fmt}\\n\\n"
        f"Content:\\n---\\n{content}\\n---\\n\\n"
        "Score this. Return JSON with: score, passed, violations, critique."
    )
    result     = call\_model("qa", system, user, max\_tokens=600)
    json\_match = re.search(r'\\{.\*\\}', result, re.DOTALL)
    if json\_match:
        try:
            data = json.loads(json\_match.group())
            data.setdefault("passed", data.get("score", 0) >= QA\_PASS\_THRESHOLD)
            return data
        except json.JSONDecodeError:
            pass
    return {"score": 0, "passed": False, "violations": \["Parse error"], "critique": result}

def run\_qa(generated: dict) -> dict:
    results = {}
    for fmt, content in generated.items():
        if not content or content.startswith("ERROR"):
            results\[fmt] = {"score": 0, "passed": False, "content": content, "violations": \["Generation failed"]}
            continue
        review          = score\_content(fmt, content)
        review\["content"] = content
        results\[fmt]    = review
    return results
```

\---

## 10\. agents/self_improve.py — The Learning Agent

After every `N` runs, this agent reads the QA score history, identifies underperforming prompt files, and rewrites them. The old version is archived.

```python
import json, os, re, shutil
from datetime import date
from pathlib import Path
from model\_router import call\_model
from utils.context\_loader import load\_brand\_context, load\_prompt
from config import (
    SELF\_IMPROVE\_EVERY\_N\_RUNS, SELF\_IMPROVE\_THRESHOLD,
    PERF\_LOG, PROMPTS\_DIR, VERSIONS\_DIR, LOGS\_DIR
)

def load\_performance\_log() -> dict:
    if not os.path.exists(PERF\_LOG):
        return {}
    with open(PERF\_LOG) as f:
        return json.load(f)

def update\_performance\_log(qa\_results: dict):
    log = load\_performance\_log()
    for fmt, result in qa\_results.items():
        if fmt not in log:
            log\[fmt] = \[]
        log\[fmt].append({
            "date":   str(date.today()),
            "score":  result.get("score", 0),
            "passed": result.get("passed", False),
        })
        # Keep only last 30 entries per format
        log\[fmt] = log\[fmt]\[-30:]
    with open(PERF\_LOG, "w") as f:
        json.dump(log, f, indent=2)

def count\_total\_runs() -> int:
    if not os.path.exists(LOGS\_DIR):
        return 0
    return len(\[f for f in os.listdir(LOGS\_DIR) if f.endswith(".json")])

def should\_run\_improvement() -> bool:
    n = count\_total\_runs()
    return n > 0 and n % SELF\_IMPROVE\_EVERY\_N\_RUNS == 0

def get\_underperforming\_formats(perf\_log: dict) -> list\[str]:
    underperforming = \[]
    for fmt, scores in perf\_log.items():
        if len(scores) < 3:
            continue
        recent\_avg = sum(s\["score"] for s in scores\[-7:]) / len(scores\[-7:])
        if recent\_avg < SELF\_IMPROVE\_THRESHOLD:
            underperforming.append((fmt, recent\_avg))
    return sorted(underperforming, key=lambda x: x\[1])  # worst first

def rewrite\_prompt(fmt: str, perf\_history: list, current\_prompt: str) -> str:
    system = (
        load\_brand\_context() + "\\n\\n"
        "You are a prompt engineering expert for the rkitect.ai content pipeline. "
        "Your job is to rewrite an underperforming agent system prompt to produce "
        "better content that scores higher on brand QA. "
        "You will be given: the current prompt, recent QA scores, and the types of violations that occurred. "
        "Rewrite the prompt to directly address the failure patterns. "
        "Return ONLY the new prompt text — no explanation, no preamble."
    )
    violations\_summary = \[]
    for entry in perf\_history\[-7:]:
        if entry.get("violations"):
            violations\_summary.extend(entry.get("violations", \[]))

    user = (
        f"FORMAT: {fmt}\\n\\n"
        f"RECENT SCORES (last 7 runs): {\[e\['score'] for e in perf\_history\[-7:]]}\\n"
        f"COMMON VIOLATIONS: {list(set(violations\_summary))}\\n\\n"
        f"CURRENT PROMPT:\\n---\\n{current\_prompt}\\n---\\n\\n"
        "Rewrite this prompt to fix the failure patterns. "
        "Keep all format-specific instructions. Tighten the voice rules. "
        "Add explicit examples of what good output looks like."
    )
    return call\_model("self\_improve", system, user, max\_tokens=3000)

def archive\_prompt(fmt: str):
    src  = os.path.join(PROMPTS\_DIR, f"{fmt}\_writer.md")
    if not os.path.exists(src):
        return
    Path(VERSIONS\_DIR).mkdir(parents=True, exist\_ok=True)
    dst  = os.path.join(VERSIONS\_DIR, f"{fmt}\_writer\_v\_{date.today()}.md")
    shutil.copy2(src, dst)
    print(f"      \[self\_improve] Archived {fmt} prompt → {dst}")

def save\_prompt(fmt: str, new\_prompt: str):
    path = os.path.join(PROMPTS\_DIR, f"{fmt}\_writer.md")
    with open(path, "w") as f:
        f.write(new\_prompt)
    print(f"      \[self\_improve] Updated {fmt} prompt.")

def run\_self\_improve(full\_qa\_results: dict = None):
    """
    Call this at the end of main.py every run.
    It updates the perf log, then checks if it's time to rewrite prompts.
    """
    # 1. Update performance log with today's QA results
    if full\_qa\_results:
        # Enrich with violation data if available
        perf\_log\_raw = load\_performance\_log()
        for fmt, result in full\_qa\_results.items():
            if fmt not in perf\_log\_raw:
                perf\_log\_raw\[fmt] = \[]
            perf\_log\_raw\[fmt].append({
                "date":       str(date.today()),
                "score":      result.get("score", 0),
                "passed":     result.get("passed", False),
                "violations": result.get("violations", \[]),
            })
            perf\_log\_raw\[fmt] = perf\_log\_raw\[fmt]\[-30:]
        with open(PERF\_LOG, "w") as f:
            json.dump(perf\_log\_raw, f, indent=2)

    # 2. Check if it's improvement day
    if not should\_run\_improvement():
        return

    print("\\n\[self\_improve] Improvement cycle triggered...")
    perf\_log       = load\_performance\_log()
    underperforming = get\_underperforming\_formats(perf\_log)

    if not underperforming:
        print("\[self\_improve] All formats above threshold. No rewrites needed.")
        return

    for fmt, avg\_score in underperforming\[:2]:  # Rewrite worst 2 formats per cycle
        print(f"\[self\_improve] Rewriting \[{fmt}] prompt (avg score: {avg\_score:.1f}/100)...")
        current\_prompt = load\_prompt(f"{fmt}\_writer")
        new\_prompt     = rewrite\_prompt(fmt, perf\_log\[fmt], current\_prompt)

        if new\_prompt and len(new\_prompt) > 200:
            archive\_prompt(fmt)
            save\_prompt(fmt, new\_prompt)
        else:
            print(f"\[self\_improve] \[{fmt}] Rewrite too short — skipping to protect prompt integrity.")
```

\---

## 11\. agents/publish.py

```python
import httpx
from config import BUFFER\_ACCESS\_TOKEN, BUFFER\_PROFILES

BUFFER\_API = "https://api.bufferapp.com/1"

def \_post\_to\_buffer(profile\_id: str, text: str) -> dict:
    if not profile\_id:
        return {"error": "No profile ID configured"}
    r = httpx.post(
        f"{BUFFER\_API}/updates/create.json",
        data={"profile\_ids\[]": profile\_id, "text": text, "now": False},
        headers={"Authorization": f"Bearer {BUFFER\_ACCESS\_TOKEN}"},
        timeout=30,
    )
    return r.json()

def run\_publish(qa\_results: dict) -> dict:
    publish\_log = {}
    platform\_map = {
        "linkedin":  "linkedin",
        "carousel":  "instagram",
        "twitter":   "twitter",
        # "reddit": "reddit",  # Uncomment once Reddit tool confirmed
    }
    for fmt, platform in platform\_map.items():
        if qa\_results.get(fmt, {}).get("passed"):
            result = \_post\_to\_buffer(
                BUFFER\_PROFILES.get(platform),
                qa\_results\[fmt]\["content"]
            )
            publish\_log\[platform] = result
            status = "queued" if result.get("success") else result.get("message", "unknown")
            print(f"      \[{platform}] Buffer: {status}")
    return publish\_log
```

\---

## 12\. main.py

```python
#!/usr/bin/env python3
import json, os, sys
from datetime import date
from pathlib import Path

from agents.research     import run\_research
from agents.filter       import run\_filter
from agents.generate     import run\_generation
from agents.qa           import run\_qa, score\_content
from agents.publish      import run\_publish
from agents.self\_improve import run\_self\_improve
from utils.context\_loader import load\_brand\_context
from config import QA\_MAX\_RETRIES, OUTPUT\_DIR, LOGS\_DIR

def save\_outputs(folder: str, data: dict):
    Path(folder).mkdir(parents=True, exist\_ok=True)
    for key, content in data.items():
        path = f"{folder}/{key}.md"
        with open(path, "w") as f:
            f.write(content if isinstance(content, str) else json.dumps(content, indent=2))

def write\_log(run\_log: dict):
    Path(LOGS\_DIR).mkdir(exist\_ok=True)
    with open(f"{LOGS\_DIR}/{date.today()}.json", "w") as f:
        json.dump(run\_log, f, indent=2)

def main():
    today   = str(date.today())
    out\_dir = f"{OUTPUT\_DIR}/{today}"
    run\_log = {"date": today, "stages": {}}

    print(f"\\n{'='\*54}")
    print(f"  rkitect.ai Content Pipeline · {today}")
    print(f"{'='\*54}\\n")

    # 1. RESEARCH
    print("\[1/6] Research agent...")
    research = run\_research()
    run\_log\["stages"]\["research"] = {"topic\_count": len(research.get("topics", \[]))}
    if not research.get("topics"):
        print("\[!] No topics found. Aborting."); write\_log(run\_log); sys.exit(1)
    print(f"      {len(research\['topics'])} topics found.")

    # 2. FILTER
    print("\[2/6] Filter agent...")
    topic = run\_filter(research)
    run\_log\["stages"]\["filter"] = topic
    if topic.get("error"):
        print(f"\[!] Filter failed. Aborting."); write\_log(run\_log); sys.exit(1)
    print(f"      → {topic.get('selected\_topic')} \[{topic.get('pillar')}]")

    # 3. GENERATE
    print("\[3/6] Generation agents (parallel)...")
    generated = run\_generation(topic)
    save\_outputs(out\_dir, generated)
    run\_log\["stages"]\["generation"] = list(generated.keys())
    print(f"      Outputs written → {out\_dir}/")

    # 4. QA with retry loop
    print("\[4/6] QA agent...")
    qa\_results = run\_qa(generated)

    for fmt in list(qa\_results.keys()):
        retries = 0
        while not qa\_results\[fmt].get("passed") and retries < QA\_MAX\_RETRIES:
            retries += 1
            critique = qa\_results\[fmt].get("critique", "")
            print(f"      \[{fmt}] score={qa\_results\[fmt].get('score')}/100 FAIL — retry {retries}/{QA\_MAX\_RETRIES}")

            from agents.generate import \_generate\_one
            \_, revised = \_generate\_one(fmt, {\*\*topic, "critique": critique}, load\_brand\_context())
            new\_review          = score\_content(fmt, revised)
            new\_review\["content"] = revised
            qa\_results\[fmt]     = new\_review

        score  = qa\_results\[fmt].get("score", 0)
        status = "PASS ✓" if qa\_results\[fmt].get("passed") else "FAIL ✗"
        print(f"      \[{fmt}] {score}/100 {status}")

    run\_log\["stages"]\["qa"] = {
        k: {"score": v.get("score"), "passed": v.get("passed")}
        for k, v in qa\_results.items()
    }

    # 5. PUBLISH
    passed = sum(1 for v in qa\_results.values() if v.get("passed"))
    print(f"\[5/6] Publishing {passed} approved pieces via Buffer...")
    publish\_log = run\_publish(qa\_results)
    run\_log\["stages"]\["publish"] = publish\_log

    # 6. SELF-IMPROVE
    print("\[6/6] Updating skill performance log...")
    run\_self\_improve(qa\_results)

    # Summary
    print(f"\\n{'─'\*54}")
    print(f"  Done · {today}")
    for fmt, r in qa\_results.items():
        icon = "✓" if r.get("passed") else "✗"
        print(f"  {icon}  {fmt:<12}  {r.get('score', 0):>3}/100")
    print(f"{'─'\*54}\\n")

    write\_log(run\_log)

if \_\_name\_\_ == "\_\_main\_\_":
    main()
```

\---

## 13\. Dashboard — dashboard/app.py

```python
from flask import Flask, render\_template, jsonify
import json, os, glob, httpx
from datetime import date, timedelta
from config import (
    DASHBOARD\_PORT, DASHBOARD\_SECRET\_KEY,
    LOGS\_DIR, OUTPUT\_DIR, PERF\_LOG,
    BUFFER\_ACCESS\_TOKEN, BUFFER\_PROFILES
)

app = Flask(\_\_name\_\_)
app.secret\_key = DASHBOARD\_SECRET\_KEY

def get\_recent\_logs(n=7):
    logs = \[]
    for path in sorted(glob.glob(f"{LOGS\_DIR}/\*.json"), reverse=True)\[:n]:
        with open(path) as f:
            logs.append(json.load(f))
    return logs

def get\_today\_output():
    folder  = f"{OUTPUT\_DIR}/{date.today()}"
    outputs = {}
    if os.path.exists(folder):
        for fname in os.listdir(folder):
            key = fname.replace(".md", "").replace(".json", "")
            with open(f"{folder}/{fname}") as f:
                outputs\[key] = f.read()
    return outputs

def get\_performance\_data():
    if not os.path.exists(PERF\_LOG):
        return {}
    with open(PERF\_LOG) as f:
        return json.load(f)

def get\_buffer\_scheduled():
    try:
        profile\_ids = \[v for v in BUFFER\_PROFILES.values() if v]
        results     = \[]
        for pid in profile\_ids:
            r = httpx.get(
                f"https://api.bufferapp.com/1/profiles/{pid}/updates/pending.json",
                headers={"Authorization": f"Bearer {BUFFER\_ACCESS\_TOKEN}"},
                timeout=10
            )
            if r.status\_code == 200:
                data = r.json()
                results.extend(data.get("updates", \[]))
        return results
    except Exception as e:
        return \[{"error": str(e)}]

@app.route("/")
def index():
    return render\_template("index.html")

@app.route("/api/data")
def api\_data():
    logs       = get\_recent\_logs()
    outputs    = get\_today\_output()
    perf       = get\_performance\_data()
    scheduled  = get\_buffer\_scheduled()

    # Compute average scores per format from perf log
    score\_summary = {}
    for fmt, entries in perf.items():
        recent = entries\[-7:]
        score\_summary\[fmt] = {
            "avg":    round(sum(e\["score"] for e in recent) / len(recent), 1) if recent else 0,
            "trend":  \[e\["score"] for e in recent],
            "passes": sum(1 for e in recent if e.get("passed")),
        }

    return jsonify({
        "today":         str(date.today()),
        "recent\_logs":   logs,
        "today\_output":  outputs,
        "score\_summary": score\_summary,
        "scheduled":     scheduled,
    })

@app.route("/api/trigger", methods=\["POST"])
def trigger\_pipeline():
    """Manually trigger a pipeline run from the dashboard."""
    import subprocess
    subprocess.Popen(\["python3", "main.py"])
    return jsonify({"status": "Pipeline triggered"})

if \_\_name\_\_ == "\_\_main\_\_":
    app.run(host="0.0.0.0", port=DASHBOARD\_PORT, debug=False)
```

\---

## 14\. Dashboard — dashboard/templates/index.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>rkitect.ai · Content Pipeline</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  </head>
  <body class="bg-gray-950 text-gray-100 font-mono min-h-screen p-6">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-bold text-white">rkitect.ai</h1>
          <p class="text-gray-500 text-sm">Content Pipeline Dashboard</p>
        </div>
        <div class="flex items-center gap-4">
          <span id="today-date" class="text-gray-500 text-sm"></span>
          <button
            onclick="triggerPipeline()"
            class="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white text-sm rounded-lg transition"
          >
            ▶ Run Now
          </button>
        </div>
      </div>

      <!-- Loading state -->
      <div id="loading" class="text-center py-20 text-gray-600">
        Loading pipeline data...
      </div>

      <div id="content" class="hidden">
        <!-- QA Score Cards -->
        <section class="mb-8">
          <h2
            class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4"
          >
            QA Scores · Last 7 Runs
          </h2>
          <div
            id="score-cards"
            class="grid grid-cols-2 md:grid-cols-4 gap-4"
          ></div>
        </section>

        <!-- Today's Topic -->
        <section class="mb-8">
          <h2
            class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4"
          >
            Today's Topic
          </h2>
          <div
            id="today-topic"
            class="bg-gray-900 rounded-xl p-5 border border-gray-800"
          ></div>
        </section>

        <!-- Generated Content Tabs -->
        <section class="mb-8">
          <h2
            class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4"
          >
            Generated Content
          </h2>
          <div
            class="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden"
          >
            <div
              id="content-tabs"
              class="flex border-b border-gray-800 overflow-x-auto"
            ></div>
            <div
              id="content-body"
              class="p-5 text-sm text-gray-300 whitespace-pre-wrap max-h-96 overflow-y-auto leading-relaxed"
            ></div>
          </div>
        </section>

        <!-- Buffer Scheduled Posts -->
        <section class="mb-8">
          <h2
            class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4"
          >
            Scheduled in Buffer
          </h2>
          <div id="buffer-posts" class="space-y-3"></div>
        </section>

        <!-- Recent Run Log -->
        <section class="mb-8">
          <h2
            class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4"
          >
            Recent Runs
          </h2>
          <div id="run-log" class="space-y-2"></div>
        </section>
      </div>
    </div>

    <script>
      let currentTab = "linkedin";
      let outputData = {};

      async function load() {
        const res  = await fetch("/api/data");
        const data = await res.json();

        document.getElementById("today-date").textContent = data.today;
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("content").classList.remove("hidden");

        renderScoreCards(data.score\_summary);
        renderTodayTopic(data.today\_output);
        renderContentTabs(data.today\_output);
        renderBufferPosts(data.scheduled);
        renderRunLog(data.recent\_logs);
        outputData = data.today\_output;
      }

      function renderScoreCards(scores) {
        const el = document.getElementById("score-cards");
        el.innerHTML = "";
        for (const \[fmt, s] of Object.entries(scores)) {
          const color = s.avg >= 80 ? "text-teal-400" : s.avg >= 70 ? "text-yellow-400" : "text-red-400";
          el.innerHTML += `
            <div class="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <div class="text-xs text-gray-500 uppercase mb-2">${fmt}</div>
              <div class="text-3xl font-bold ${color}">${s.avg}<span class="text-sm text-gray-600">/100</span></div>
              <div class="text-xs text-gray-600 mt-1">${s.passes}/7 passed</div>
            </div>`;
        }
      }

      function renderTodayTopic(outputs) {
        const el = document.getElementById("today-topic");
        const topicRaw = outputs\["topics"] || "";
        try {
          const t = JSON.parse(topicRaw);
          el.innerHTML = `
            <div class="text-white font-bold mb-1">${t.selected\_topic || "No topic yet"}</div>
            <div class="text-xs text-teal-400 mb-3">${t.pillar || ""}</div>
            <div class="text-gray-400 text-sm">${t.angle || ""}</div>`;
        } catch {
          el.innerHTML = `<div class="text-gray-600 text-sm">No run today yet.</div>`;
        }
      }

      function renderContentTabs(outputs) {
        const tabs = \["linkedin", "carousel", "reel", "twitter", "reddit"];
        const tabEl = document.getElementById("content-tabs");
        const bodyEl = document.getElementById("content-body");
        tabEl.innerHTML = "";

        tabs.forEach(t => {
          if (!outputs\[t]) return;
          const btn = document.createElement("button");
          btn.textContent = t;
          btn.className = `px-4 py-3 text-xs uppercase tracking-wide transition ${
            t === currentTab
              ? "text-teal-400 border-b-2 border-teal-400 bg-gray-800"
              : "text-gray-500 hover:text-gray-300"
          }`;
          btn.onclick = () => {
            currentTab = t;
            renderContentTabs(outputs);
          };
          tabEl.appendChild(btn);
        });

        bodyEl.textContent = outputs\[currentTab] || "No content generated yet for this format.";
      }

      function renderBufferPosts(posts) {
        const el = document.getElementById("buffer-posts");
        if (!posts || posts.length === 0) {
          el.innerHTML = `<div class="text-gray-600 text-sm">No scheduled posts found.</div>`;
          return;
        }
        el.innerHTML = posts.slice(0, 10).map(p => `
          <div class="bg-gray-900 rounded-lg p-4 border border-gray-800 flex gap-4">
            <span class="text-xs text-teal-400 uppercase w-20 flex-shrink-0">${p.profile\_service || "buffer"}</span>
            <span class="text-sm text-gray-300 truncate">${(p.text || "").slice(0, 100)}…</span>
            <span class="text-xs text-gray-600 flex-shrink-0">${p.due\_time || ""}</span>
          </div>`).join("");
      }

      function renderRunLog(logs) {
        const el = document.getElementById("run-log");
        el.innerHTML = logs.slice(0, 7).map(log => {
          const qa = log.stages?.qa || {};
          const scores = Object.entries(qa).map((\[fmt, d]) =>
            `<span class="${d.passed ? 'text-teal-400' : 'text-red-400'}">${fmt} ${d.score}</span>`
          ).join("  ");
          return `
            <div class="bg-gray-900 rounded-lg px-4 py-3 border border-gray-800 flex items-center gap-6 text-xs">
              <span class="text-gray-500 w-24 flex-shrink-0">${log.date}</span>
              <span class="text-gray-400 flex-shrink-0">${log.stages?.filter?.selected\_topic?.slice(0, 40) || "—"}…</span>
              <div class="flex gap-3 ml-auto">${scores}</div>
            </div>`;
        }).join("");
      }

      async function triggerPipeline() {
        if (!confirm("Trigger a pipeline run now?")) return;
        await fetch("/api/trigger", { method: "POST" });
        alert("Pipeline triggered. Check back in a few minutes.");
      }

      load();
      setInterval(load, 60000);  // Refresh every 60 seconds
    </script>
  </body>
</html>
```

\---

## 15\. Running the Dashboard

```bash
# Start the dashboard (run this on your VM, keep it alive with screen or tmux)
cd rkitect-pipeline
python3 dashboard/app.py

# Or run it as a background service
nohup python3 dashboard/app.py > /var/log/rkitect-dashboard.log 2>\&1 \&
```

Access it at `http://YOUR\_VM\_IP:5050`

To expose it securely, add Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server\_name dashboard.rkitect.ai;

    location / {
        proxy\_pass http://127.0.0.1:5050;
        proxy\_set\_header Host $host;
    }
}
```

\---

## 16\. Cron Setup

```bash
crontab -e
```

```cron
# Pipeline — runs at 6am daily
0 6 \* \* \* cd /home/ubuntu/rkitect-pipeline \&\& python3 main.py >> /var/log/rkitect-pipeline.log 2>\&1

# Dashboard — starts on reboot
@reboot cd /home/ubuntu/rkitect-pipeline \&\& python3 dashboard/app.py >> /var/log/rkitect-dashboard.log 2>\&1
```

\---

## 17\. Cost Breakdown (Approximate Per Day)

| Task            | Model                | Est. Tokens | Est. Cost                    |
| --------------- | -------------------- | ----------- | ---------------------------- |
| Research        | moonshotai/kimi-k2.6 | \~3,000     | \~$0.001                     |
| Filter          | Mistral 7B           | \~1,000     | \~$0.0002                    |
| LinkedIn        | Claude Sonnet        | \~1,500     | \~$0.005                     |
| Carousel        | GPT-4o-mini          | \~1,500     | \~$0.0003                    |
| Reel            | GPT-4o-mini          | \~1,000     | \~$0.0002                    |
| Twitter         | Mistral 7B           | \~800       | \~$0.0001                    |
| QA (×5 formats) | Claude Sonnet        | \~4,000     | \~$0.012                     |
| **Total**       |                      |             | **\~$0.02/day · \~$7/month** |

Running everything on Claude Sonnet would cost \~$0.08/day (\~$25/month). The model routing saves \~75% with no meaningful quality drop on the lighter tasks.

\---

## 18\. requirements.txt

```
anthropic>=0.25.0
openai>=1.30.0
httpx>=0.27.0
python-dotenv>=1.0.0
flask>=3.0.0
```

\---

_rkitect.ai · HappyMonk AI · Bengaluru · May 2026 · v2_
