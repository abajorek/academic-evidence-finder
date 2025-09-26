"""Utilities for scoring provenance evidence from email metadata."""

from email.utils import getaddresses
from typing import Iterable, Mapping, Optional, Sequence, Tuple


class ProvenanceScorer:
    """Score artifacts using email provenance information."""

    EMAIL_HEADER_PRECEDENCE: Sequence[tuple[str, str]] = (
        ("from", "From"),
        ("sender", "Sender"),
        ("reply-to", "Reply-To"),
    )

    def __init__(self, target_emails: Iterable[str], email_score: float = 1.0) -> None:
        self._target_emails = {
            self._normalize_email(email)
            for email in target_emails
            if email
        }
        self.email_score = email_score

    @staticmethod
    def _normalize_email(address: str) -> str:
        return address.strip().lower()

    @staticmethod
    def _normalize_headers(headers: Mapping[str, str]) -> Mapping[str, str]:
        return {key.lower(): value for key, value in headers.items() if isinstance(value, str)}

    def _score_email(self, headers: Mapping[str, str]) -> Tuple[float, Optional[str]]:
        """Score email provenance headers.

        Returns a tuple of the awarded score and an evidence note. The note documents
        the precedence of headers examined and which header produced a match.
        """

        if not self._target_emails or not headers:
            return 0.0, None

        normalized_headers = self._normalize_headers(headers)
        precedence_display = " > ".join(display for _, display in self.EMAIL_HEADER_PRECEDENCE)

        for header_key, display_name in self.EMAIL_HEADER_PRECEDENCE:
            candidate_values = []
            if header_key in normalized_headers:
                candidate_values.append(normalized_headers[header_key])
            if header_key == "reply-to":
                for alias in ("reply_to", "replyto"):
                    if alias in normalized_headers:
                        candidate_values.append(normalized_headers[alias])

            for raw_value in candidate_values:
                for _, address in getaddresses([raw_value]):
                    normalized_address = self._normalize_email(address)
                    if normalized_address and normalized_address in self._target_emails:
                        note = (
                            f"Matched {display_name} header ({normalized_address}) while "
                            f"checking precedence {precedence_display}."
                        )
                        return self.email_score, note

        return 0.0, None

