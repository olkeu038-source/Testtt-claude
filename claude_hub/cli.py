"""Terminal chat. Run with: python -m claude_hub.cli"""

from .client import ask
from .store import MODELS, load_settings, save_settings

HELP = "Commands: /model <name>  /models  /clear  /quit"


def main():
    history = []
    print("Claude terminal chat.")
    print(HELP + "\n")

    while True:
        try:
            text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not text:
            continue
        if text == "/quit":
            break
        if text == "/clear":
            history.clear()
            print("(conversation cleared)\n")
            continue
        if text == "/models":
            print("Available models: " + ", ".join(MODELS) + "\n")
            continue
        if text.startswith("/model"):
            parts = text.split()
            if len(parts) == 2 and parts[1] in MODELS:
                settings = load_settings()
                settings["model"] = parts[1]
                save_settings(settings)
                print(f"(model set to {parts[1]})\n")
            else:
                print("Usage: /model <name>. Run /models to see names.\n")
            continue

        history.append({"role": "user", "content": text})
        try:
            reply = ask(history)
        except Exception as error:  # show API errors without crashing the chat
            history.pop()
            print(f"(error: {error})\n")
            continue

        history.append({"role": "assistant", "content": reply})
        print(f"\nclaude> {reply}\n")


if __name__ == "__main__":
    main()
