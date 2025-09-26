"""Tests for the email provenance scorer."""

import json
from pathlib import Path

import pytest

from ae_finder.provenance import ProvenanceScorer

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_score_email_prefers_from_header():
    scorer = ProvenanceScorer(["author@example.edu"], email_score=2.0)
    headers = {
        "From": "Author Example <author@example.edu>",
        "Sender": "Department Bot <bot@example.edu>",
        "Reply-To": "assistant@example.edu",
    }

    score, note = scorer._score_email(headers)
    assert score == pytest.approx(2.0)
    assert note is not None
    assert "From" in note
    assert "From > Sender > Reply-To" in note


def test_score_email_falls_back_to_sender_header(tmp_path: Path):
    fixture = load_fixture("email_sender.json")
    scorer = ProvenanceScorer(["bot@example.edu"])

    score, note = scorer._score_email(fixture["headers"])

    assert score == pytest.approx(1.0)
    assert note is not None
    assert "Sender" in note
    assert "bot@example.edu" in note
    assert "From > Sender > Reply-To" in note


def test_score_email_falls_back_to_reply_to_header():
    fixture = load_fixture("email_reply_to.json")
    scorer = ProvenanceScorer(["prof@example.edu"])

    score, note = scorer._score_email(fixture["headers"])

    assert score == pytest.approx(1.0)
    assert note is not None
    assert "Reply-To" in note
    assert "prof@example.edu" in note
    assert "From > Sender > Reply-To" in note


def test_score_email_ignores_non_matching_headers():
    headers = {
        "From": "Different Person <other@example.edu>",
        "Sender": "Department Bot <bot@example.edu>",
        "Reply-To": "Assistant Example <assistant@example.edu>",
    }
    scorer = ProvenanceScorer(["prof@example.edu"])

    score, note = scorer._score_email(headers)

    assert score == pytest.approx(0.0)
    assert note is None


def test_score_email_handles_aliases_for_reply_to():
    headers = {
        "reply_to": "Professor Example <prof@example.edu>",
    }
    scorer = ProvenanceScorer(["prof@example.edu"])

    score, note = scorer._score_email(headers)

    assert score == pytest.approx(1.0)
    assert note is not None
    assert "Reply-To" in note
    assert "prof@example.edu" in note
