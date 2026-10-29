"""Admin panel. Run with: python -m claude_hub.admin

Opens at http://127.0.0.1:5000 and asks for ADMIN_PASSWORD. If that variable
is not set, a random password is generated and printed at startup.
"""

import os
import secrets
from functools import wraps

from flask import Flask, Response, redirect, render_template_string, request, url_for

from .store import (
    MODELS,
    get_api_key,
    load_memory,
    load_settings,
    save_memory,
    save_settings,
    set_api_key,
)

app = Flask(__name__)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or secrets.token_urlsafe(12)


def require_login(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not secrets.compare_digest(auth.password or "", ADMIN_PASSWORD):
            return Response(
                "Admin login required.",
                401,
                {"WWW-Authenticate": 'Basic realm="Claude Hub admin"'},
            )
        return view(*args, **kwargs)

    return wrapper


def masked_key():
    key = get_api_key()
    if not key:
        return "not set"
    return f"{key[:7]}…{key[-4:]}" if len(key) > 12 else "set"


PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claude Hub admin</title>
<style>
  :root { --bg:#faf9f5; --card:#fff; --ink:#1f1e1d; --muted:#6b6a68; --accent:#c96442; --line:#e5e3dc; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#262624; --card:#30302e; --ink:#f0eee6; --muted:#a8a6a0; --accent:#e08a6d; --line:#444440; }
  }
  body { margin:0; font-family:system-ui,sans-serif; background:var(--bg); color:var(--ink); }
  main { max-width:760px; margin:0 auto; padding:16px; }
  h1 { font-size:1.5rem; }
  section { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px; margin-bottom:16px; }
  h2 { font-size:1.1rem; margin-top:0; }
  label { display:block; font-weight:600; margin:10px 0 4px; }
  input, select, textarea { width:100%; box-sizing:border-box; padding:8px; font:inherit; color:var(--ink);
    background:var(--bg); border:1px solid var(--line); border-radius:8px; }
  textarea { min-height:120px; }
  button { margin-top:12px; padding:8px 14px; font:inherit; border:0; border-radius:8px; background:var(--accent); color:#fff; cursor:pointer; }
  button.danger { background:#a33; }
  ul { padding-left:18px; }
  li { margin:6px 0; }
  .muted { color:var(--muted); font-size:.9rem; }
  form.inline { display:inline; margin:0; }
  form.inline button { margin:0 0 0 8px; padding:2px 8px; font-size:.85rem; }
</style>
</head>
<body>
<main>
  <h1>Claude Hub admin</h1>

  <section>
    <h2>Model and behaviour</h2>
    <form method="post" action="{{ url_for('save_model') }}">
      <label for="model">Model</label>
      <select id="model" name="model">
        {% for m in models %}
          <option value="{{ m }}" {% if m == settings.model %}selected{% endif %}>{{ m }}</option>
        {% endfor %}
      </select>
      <label for="max_tokens">Max reply tokens</label>
      <input id="max_tokens" name="max_tokens" type="number" min="1" max="8192" value="{{ settings.max_tokens }}">
      <label for="system_prompt">System prompt</label>
      <textarea id="system_prompt" name="system_prompt">{{ settings.system_prompt }}</textarea>
      <button type="submit">Save settings</button>
    </form>
  </section>

  <section>
    <h2>Memory notes</h2>
    <p class="muted">Each note is added to the system prompt, so Claude sees it in every chat.</p>
    {% if notes %}
    <ul>
      {% for note in notes %}
      <li>
        {{ note }}
        <form class="inline" method="post" action="{{ url_for('delete_note', idx=loop.index0) }}">
          <button class="danger" type="submit">Delete</button>
        </form>
      </li>
      {% endfor %}
    </ul>
    {% else %}
    <p class="muted">No notes yet.</p>
    {% endif %}
    <form method="post" action="{{ url_for('add_note') }}">
      <label for="note">New note</label>
      <input id="note" name="note" type="text" maxlength="500" placeholder="e.g. I write in British English">
      <button type="submit">Add note</button>
    </form>
  </section>

  <section>
    <h2>API key</h2>
    <p class="muted">Current key: {{ key_status }}. The full key is never shown here.
      A key set in the ANTHROPIC_API_KEY environment variable overrides this one.</p>
    <form method="post" action="{{ url_for('save_key') }}">
      <label for="api_key">New API key</label>
      <input id="api_key" name="api_key" type="password" autocomplete="off" placeholder="sk-ant-…">
      <button type="submit">Save key</button>
    </form>
  </section>
</main>
</body>
</html>
"""


@app.get("/")
@require_login
def index():
    return render_template_string(
        PAGE,
        models=MODELS,
        settings=load_settings(),
        notes=load_memory(),
        key_status=masked_key(),
    )


@app.post("/settings")
@require_login
def save_model():
    settings = load_settings()
    if request.form.get("model") in MODELS:
        settings["model"] = request.form["model"]
    try:
        settings["max_tokens"] = min(max(int(request.form["max_tokens"]), 1), 8192)
    except (KeyError, ValueError):
        pass
    settings["system_prompt"] = request.form.get("system_prompt", "").strip()
    save_settings(settings)
    return redirect(url_for("index"))


@app.post("/memory")
@require_login
def add_note():
    note = request.form.get("note", "").strip()
    if note:
        notes = load_memory()
        notes.append(note[:500])
        save_memory(notes)
    return redirect(url_for("index"))


@app.post("/memory/<int:idx>/delete")
@require_login
def delete_note(idx):
    notes = load_memory()
    if 0 <= idx < len(notes):
        del notes[idx]
        save_memory(notes)
    return redirect(url_for("index"))


@app.post("/key")
@require_login
def save_key():
    key = request.form.get("api_key", "").strip()
    if key:
        set_api_key(key)
    return redirect(url_for("index"))


if __name__ == "__main__":
    host = os.environ.get("ADMIN_HOST", "127.0.0.1")
    print(f"Admin panel: http://{host}:5000")
    print(f"Login password: {ADMIN_PASSWORD}" + ("" if os.environ.get("ADMIN_PASSWORD") else "  (generated; set ADMIN_PASSWORD to keep your own)"))
    app.run(host=host, port=5000)
