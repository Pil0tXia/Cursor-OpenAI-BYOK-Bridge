"""Tests for upstream URL resolution."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from byok.proxy import resolve_upstream_url  # noqa: E402


class ResolveUpstreamUrlTests(unittest.TestCase):
    @patch(
        "byok.proxy.config.UPSTREAM_RESPONSES_API_URL",
        "https://api.example.com/v1/responses",
    )
    def test_responses_compat_dedupes_v1_prefix(self) -> None:
        url = resolve_upstream_url("/v1/responses", "responses-compat")
        self.assertEqual(url, "https://api.example.com/v1/responses")

    @patch(
        "byok.proxy.config.UPSTREAM_RESPONSES_API_URL",
        "https://api.example.com/v1/responses",
    )
    def test_chat_completions_dedupes_v1_prefix(self) -> None:
        url = resolve_upstream_url("/v1/chat/completions", "chat-completions")
        self.assertEqual(url, "https://api.example.com/v1/chat/completions")

    @patch(
        "byok.proxy.config.UPSTREAM_RESPONSES_API_URL",
        "https://api.example.com/v1/responses",
    )
    def test_path_without_v1_prefix_is_unchanged(self) -> None:
        url = resolve_upstream_url("/responses", "responses-compat")
        self.assertEqual(url, "https://api.example.com/v1/responses")

    @patch(
        "byok.proxy.config.UPSTREAM_RESPONSES_API_URL",
        "https://api.openai.com/v1/chat/completions",
    )
    def test_chat_completions_upstream_endpoint(self) -> None:
        url = resolve_upstream_url("/v1/chat/completions", "chat-completions")
        self.assertEqual(url, "https://api.openai.com/v1/chat/completions")


if __name__ == "__main__":
    unittest.main()
