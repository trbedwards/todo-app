import sys
from pathlib import Path

# Ensure repository root is on the import path when running tests
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.db import get_session
from sqlmodel import Session


def test_get_session_yields_session():
    gen = get_session()
    session = next(gen)
    try:
        assert isinstance(session, Session)
    finally:
        gen.close()
