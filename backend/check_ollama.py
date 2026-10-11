#!/usr/bin/env python
"""
Preflight Diagnostic Script for Local Ollama LLM
Checks:
1. Whether Ollama CLI is installed and in PATH.
2. Whether the Ollama service is running and accessible over HTTP.
3. Retrieves all locally installed models.
4. Verifies whether the configured model exists.
5. Displays exact pull command if missing.
6. Displays startup instructions if Ollama is not running.
"""

import sys
import shutil
from app.config import settings
from app.services.llm.ollama import check_ollama_startup

def main():
    print("=" * 65)
    print(" NoteTube - Ollama Local Setup Preflight Checker")
    print("=" * 65)
    print(f"Target Base URL     : {settings.OLLAMA_BASE_URL}")
    print(f"Configured Model    : {settings.OLLAMA_MODEL}")
    print(f"Configured Provider : {settings.LLM_PROVIDER}")
    print("-" * 65)

    res = check_ollama_startup(
        base_url=settings.OLLAMA_BASE_URL,
        configured_model=settings.OLLAMA_MODEL
    )

    # 1. CLI installed
    if res["cli_installed"]:
        print("[PASS] 1. Ollama CLI is installed and accessible in system PATH.")
    else:
        print("[WARN] 1. 'ollama' executable not found in PATH (if running as a desktop app, this may still work).")

    # 2. Service running
    if res["service_running"]:
        print(f"[PASS] 2. Ollama HTTP service is RUNNING at {res['base_url']}.")
    else:
        print(f"[FAIL] 2. Ollama service is NOT accessible at {res['base_url']}.")
        print("\n" + "=" * 65)
        print(" ACTION REQUIRED: START OLLAMA")
        print("=" * 65)
        print(res["message"])
        sys.exit(1)

    # 3. List installed models
    models = res["installed_models"]
    print(f"[PASS] 3. Retrieved {len(models)} installed model(s):")
    if models:
        for m in models:
            marker = " (Configured Model)" if m == res["configured_model"] or m.startswith(res["configured_model"] + ":") else ""
            print(f"         - {m}{marker}")
    else:
        print("         (No models currently installed)")

    # 4. Configured model exists
    if res["model_exists"]:
        print(f"[PASS] 4. Configured model '{res['configured_model']}' is installed and READY.")
        print("-" * 65)
        print(">> ALL PREFLIGHT CHECKS PASSED!")
        print(">> NoteTube is ready to run completely locally without cloud API keys.")
        print("=" * 65)
        sys.exit(0)
    else:
        print(f"[FAIL] 4. Configured model '{res['configured_model']}' was NOT found.")
        print("\n" + "=" * 65)
        print(f" ACTION REQUIRED: DOWNLOAD MODEL '{res['configured_model']}'")
        print("=" * 65)
        print(f"Run the following command in your terminal:")
        print(f"\n    {res['suggested_command']}\n")
        print("Once the download completes, rerun this check or start NoteTube.")
        print("=" * 65)
        sys.exit(1)

if __name__ == "__main__":
    main()
