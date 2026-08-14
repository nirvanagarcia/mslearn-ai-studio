"""
Preflight check for the Wingtip Journeys "Build a generative AI chat app" lab.

WORKING DIRECTORY: run this from the STARTER code folder --
    labfiles/B-build-a-generative-ai-chat-app/python
which is the folder you opened a terminal in and created your virtual
environment in. From there the script is one level up, so the path is
"../setup/check_env.py". There is no setup/ folder inside Solution/, so
this does NOT work from Solution/python.

Each task in this lab can be completed on its own. Before you start a task,
run this script to confirm your .env file has everything that task needs:

    cd labfiles/B-build-a-generative-ai-chat-app/python
    python ../setup/check_env.py --task 2

It never changes anything - it only reads your .env (and, for Task 4, the local
destination guides) and tells you what is missing, so you can fix it before
running the task.

Tasks and what they need:

    Task 1  (code)  AZURE_OPENAI_ENDPOINT, MODEL_DEPLOYMENT
    Task 2  (code)  AZURE_OPENAI_ENDPOINT, MODEL_DEPLOYMENT
    Task 3  (code)  AZURE_OPENAI_ENDPOINT, MODEL_DEPLOYMENT
    Task 4  (code)  AZURE_OPENAI_ENDPOINT, MODEL_DEPLOYMENT, plus the guides/ folder
"""

import argparse
import os
from pathlib import Path


def _find_closing_quote(text, quote, start=0):
    """Index of the next closing `quote` in `text`, ignoring backslash-escaped ones.

    Only double quotes honour escapes, matching dotenv: inside single quotes a
    backslash is a literal character, so \\' still closes the value.
    """
    index = start
    while index < len(text):
        char = text[index]
        if char == "\\" and quote == '"' and index + 1 < len(text):
            index += 2
            continue
        if char == quote:
            return index
        index += 1
    return -1


def _decode_double_quoted(value):
    """Apply the backslash escapes python-dotenv honours inside double quotes."""
    escapes = {
        "\\": "\\", "'": "'", '"': '"', "a": "\a", "b": "\b",
        "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v",
    }
    out = []
    index = 0
    while index < len(value):
        char = value[index]
        if char == "\\" and index + 1 < len(value) and value[index + 1] in escapes:
            out.append(escapes[value[index + 1]])
            index += 2
        else:
            out.append(char)
            index += 1
    return "".join(out)


def _parse_env_file(path):
    """Minimal .env reader used when python-dotenv isn't importable.

    Matches dotenv.dotenv_values for the syntax a lab .env can contain:

    * blank lines and # comments are skipped
    * an "export " prefix is stripped
    * a key with no "=" maps to None
    * a quoted value keeps any # inside the quotes; an unquoted value drops a
      trailing " #" comment, and a quoted one drops anything after the closing quote
    * a value opened with a quote may span lines, and the newlines are kept
    * an entry whose quote is never closed is DISCARDED, as dotenv does, so a
      malformed .env is reported as missing rather than silently accepted
    * inside double quotes, backslash escapes (\\n, \\", \\\\, ...) are decoded;
      single-quoted values are raw

    Opened as utf-8-sig so a Notepad-saved file's BOM is consumed rather than
    becoming part of the first key name.
    """
    with open(path, encoding="utf-8-sig") as handle:
        lines = handle.read().splitlines()

    values = {}
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        if "=" not in line:
            values[line] = None
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        quote = value[0] if value[:1] in ('"', "'") else ""
        if not quote:
            # Unquoted: a " #" starts a trailing comment.
            values[key] = value.split(" #", 1)[0].rstrip()
            continue

        body = value[1:]
        end = _find_closing_quote(body, quote)
        while end == -1 and index < len(lines):
            # Quote still open: keep taking whole lines, preserving the newlines.
            resume = len(body) + 1
            body += "\n" + lines[index]
            index += 1
            end = _find_closing_quote(body, quote, resume)
        if end == -1:
            # Never closed, even at EOF: drop the entry, matching dotenv.
            continue
        body = body[:end]
        values[key] = _decode_double_quoted(body) if quote == '"' else body

    return values


try:
    from dotenv import dotenv_values
except ImportError:
    # python-dotenv lives in the lab's virtual environment. This check should still
    # work if you run it before "pip install -r requirements.txt", so fall back to
    # the equivalent stdlib reader defined above.
    dotenv_values = _parse_env_file


KNOWN_KEYS = ("AZURE_OPENAI_ENDPOINT", "MODEL_DEPLOYMENT")

# Which .env keys each task needs to run on its own.
TASK_REQUIREMENTS = {
    1: ["AZURE_OPENAI_ENDPOINT", "MODEL_DEPLOYMENT"],
    2: ["AZURE_OPENAI_ENDPOINT", "MODEL_DEPLOYMENT"],
    3: ["AZURE_OPENAI_ENDPOINT", "MODEL_DEPLOYMENT"],
    4: ["AZURE_OPENAI_ENDPOINT", "MODEL_DEPLOYMENT"],
}

# Tasks that also need the local grounding data.
TASKS_NEEDING_GUIDES = {4}

# Placeholder text shipped in .env.example - present but not yet filled in.
PLACEHOLDERS = {
    "",
    "your_azure_openai_endpoint",
    "your_model_deployment",
    "<your_azure_openai_endpoint>",
    "<your_model_deployment>",
}

# How to fix each key, shown only when it's missing.
FIX_HINTS = {
    "AZURE_OPENAI_ENDPOINT": (
        "Copy the Azure OpenAI Endpoint (not the project endpoint) from your project "
        "home page in the Microsoft Foundry portal, then set AZURE_OPENAI_ENDPOINT in .env."
    ),
    "MODEL_DEPLOYMENT": (
        "Set MODEL_DEPLOYMENT to the exact name of your deployed model (for example, "
        "gpt-5.2). You can see it in the Foundry portal under Deployments."
    ),
}


def find_env_file():
    """Return the .env next to the lab's python folder, wherever this is run from."""
    here = Path(__file__).resolve().parent
    candidates = [
        Path.cwd() / ".env",
        here.parent / "python" / ".env",
        here.parent / ".env",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    # Default to the python-folder location even if it doesn't exist yet.
    return here.parent / "python" / ".env"


def find_guides_folder():
    """Return the guides folder used by Task 4, wherever this is run from."""
    here = Path(__file__).resolve().parent
    candidates = [
        Path.cwd() / "guides",
        here.parent / "python" / "guides",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return here.parent / "python" / "guides"


def has_utf8_bom(env_path):
    """True if the .env starts with a UTF-8 BOM.

    Notepad (and other Windows editors) default to "UTF-8 with BOM". The BOM
    becomes part of the first key name, so load_dotenv() sets "\\ufeffKEY" and
    the app's os.getenv("KEY") returns None. It's a real defect that breaks the
    app, so it's reported rather than silently tolerated.
    """
    try:
        with open(env_path, "rb") as handle:
            return handle.read(3) == b"\xef\xbb\xbf"
    except OSError:
        return False


def load_values(env_path):
    """Merge real environment variables over .env file values (env wins).

    A leading UTF-8 BOM is stripped from key names so the per-key report below
    stays readable; the BOM itself is reported separately by has_utf8_bom,
    because it still has to be fixed for the app to work.
    """
    values = {}
    if env_path.exists():
        try:
            parsed = dotenv_values(env_path)
        except OSError:
            # Unreadable (permissions, a directory, a half-written file): treat
            # it as empty and let the per-key report say what's missing.
            parsed = {}
        for key, value in parsed.items():
            if value is None:
                continue
            values[key.lstrip("\ufeff").removeprefix("export ").strip()] = value
    for key in KNOWN_KEYS:
        if os.environ.get(key):
            values[key] = os.environ[key]
    return values


def is_set(values, key):
    """A key counts as set if it's present and not a leftover placeholder."""
    value = (values.get(key) or "").strip().strip('"')
    return bool(value) and value not in PLACEHOLDERS


def main():
    parser = argparse.ArgumentParser(
        description="Check that your .env has what a given lab task needs."
    )
    parser.add_argument(
        "--task",
        type=int,
        choices=sorted(TASK_REQUIREMENTS),
        required=True,
        help="Which task you're about to start (1-4).",
    )
    args = parser.parse_args()

    env_path = find_env_file()
    values = load_values(env_path)
    required = TASK_REQUIREMENTS[args.task]

    print(f"Checking readiness for Task {args.task}")
    print(f"Reading: {env_path}{'' if env_path.exists() else '  (not found yet)'}")
    print()

    missing = [key for key in required if not is_set(values, key)]

    for key in required:
        mark = "OK " if is_set(values, key) else "MISSING"
        print(f"  [{mark}] {key}")

    guides_problem = None
    if args.task in TASKS_NEEDING_GUIDES:
        guides = find_guides_folder()
        guide_files = sorted(guides.glob("*.md")) if guides.is_dir() else []
        if guide_files:
            print(f"  [OK ] guides/ ({len(guide_files)} destination guides)")
        else:
            print("  [MISSING] guides/")
            guides_problem = (
                "Task 4 uploads the Wingtip Journeys destination guides to a vector store. "
                f"Expected Markdown files in {guides}. Re-clone the mslearn-ai-studio repo "
                "if the folder is missing."
            )

    bom_problem = None
    if env_path.exists() and has_utf8_bom(env_path):
        print("  [PROBLEM] .env starts with a UTF-8 BOM")
        bom_problem = (
            "Your .env was saved as 'UTF-8 with BOM' (Notepad does this by default). "
            "The BOM becomes part of the first setting's name, so the app reads it as "
            "empty even though the file looks correct. Re-save the file as plain UTF-8: "
            "in VS Code, click the encoding in the status bar, choose 'Save with Encoding', "
            "then 'UTF-8' (not 'UTF-8 with BOM')."
        )

    if not missing and guides_problem is None and bom_problem is None:
        print()
        print(f"You're ready to start Task {args.task}.")
        return 0

    print()
    print("Fix the following before starting this task:")
    for key in missing:
        print(f"\n  {key}\n    {FIX_HINTS.get(key, 'Add this key to your .env file.')}")
    if guides_problem is not None:
        print(f"\n  guides/\n    {guides_problem}")
    if bom_problem is not None:
        print(f"\n  .env encoding\n    {bom_problem}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
