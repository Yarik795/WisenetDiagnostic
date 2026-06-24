#!/usr/bin/env python3
"""Remove chat sessions that have no messages."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.chat_store import ChatStore


def main() -> int:
    store = ChatStore()
    store.init_db()
    removed = store.delete_empty_sessions()
    print(f"Removed {removed} empty chat session(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
