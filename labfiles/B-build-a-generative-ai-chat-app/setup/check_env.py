"""
Preflight check for the Wingtip Journeys "Build a generative AI chat app" lab.

Each task in this lab can be completed on its own. Before you start a task,
run this script to confirm your .env file has everything that task needs.
Run it from the `python` folder you work in, with your virtual environment
active:

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

try:
    from dotenv import dotenv_values
except ImportError:
    # python-dotenv lives in the lab's virtual environment. This check should still
    # work if you run it before "pip install -r requirements.txt", so fall back to a
    # minimal reader that handles the simple KEY=value lines a lab .env contains.
    def dotenv_values(path):
        values = {}
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip().strip('"').strip("'")
        return values


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


def load_values(env_path):
    """Merge real environment variables over .env file values (env wins)."""
    values = {}
    if env_path.exists():
        values.update({k: v for k, v in dotenv_values(env_path).items() if v is not None})
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

    if not missing and guides_problem is None:
        print()
        print(f"You're ready to start Task {args.task}.")
        return 0

    print()
    print("Set the following before starting this task:")
    for key in missing:
        print(f"\n  {key}\n    {FIX_HINTS.get(key, 'Add this key to your .env file.')}")
    if guides_problem is not None:
        print(f"\n  guides/\n    {guides_problem}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
