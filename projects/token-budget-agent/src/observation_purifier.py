"""
ObservationPurifier — Strips low-information content from tool outputs 
before they enter the LLM context window.

Design principle: cheap signals only. No LLM calls, no model inference.
Uses structural heuristics:
- Truncates oversized outputs (>N chars)
- Strips boilerplate (stack traces with no error, status: OK, timestamps)
- Deduplicates repeated content (JSON arrays of identical structs)
- Extracts salient summary fields from structured data
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class PurificationConfig:
    """Configuration for observation purification behavior."""
    max_chars: int = 4_000           # max chars per observation
    max_json_keys: int = 10           # max keys in JSON before truncation
    max_array_items: int = 20         # max array items before summarization
    strip_timestamps: bool = True     # remove ISO timestamp fields
    strip_success_fields: bool = True # remove 'status: OK/success' boilerplate
    strip_stack_traces: bool = False  # keep stack traces by default (debug info)
    deduplicate_lines: bool = True    # remove consecutive duplicate lines
    summary_fallback: str = "[Truncated: {original_chars} chars → {new_chars} chars]"


# Patterns for low-information content
_TIMESTAMP_PATTERN = re.compile(
    r'\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?\b'
)
_SUCCESS_PATTERNS = [
    re.compile(r'^\s*"?(status|success|result)"?\s*[:=]\s*"?(ok|true|success|done)"?\s*,?\s*$', re.IGNORECASE),
    re.compile(r'^\s*"?(error|errors)"?\s*[:=]\s*null\s*,?\s*$', re.IGNORECASE),
    re.compile(r'^\s*"?(code|exit_code|exitcode)"?\s*[:=]\s*0\s*,?\s*$'),
]
_EMPTY_LINE = re.compile(r'^\s*$')


class ObservationPurifier:
    """Purifies tool outputs by removing low-information content."""

    def __init__(self, config: Optional[PurificationConfig] = None):
        self.config = config or PurificationConfig()

    def purify(self, observation: str, tool_name: str = "") -> str:
        """Purify a single observation string.
        
        Returns the purified observation with a truncation notice if applicable.
        """
        if not observation:
            return observation
        
        result = observation
        
        # 1. Strip boilerplate status lines
        if self.config.strip_success_fields:
            result = self._strip_success_lines(result)
        
        # 2. Strip timestamps (line-level removal)
        if self.config.strip_timestamps:
            result = self._strip_timestamp_lines(result)
        
        # 3. Deduplicate consecutive identical lines
        if self.config.deduplicate_lines:
            result = self._deduplicate_lines(result)
        
        # 4. Handle structured data (JSON)
        result = self._purify_structured(result, tool_name)
        
        # 5. Final length cap
        if len(result) > self.config.max_chars:
            original_len = len(result)
            result = result[:self.config.max_chars]
            notice = self.config.summary_fallback.format(
                original_chars=original_len,
                new_chars=len(result),
            )
            result += f"\n\n{notice}"
        
        return result
    
    def purify_batch(
        self, observations: list[tuple[str, str]]
    ) -> list[tuple[str, str]]:
        """Purify a batch of (tool_name, observation) pairs."""
        return [
            (name, self.purify(obs, name))
            for name, obs in observations
        ]

    def _strip_success_lines(self, text: str) -> str:
        """Remove lines that are boilerplate success/status indicators."""
        lines = text.split('\n')
        filtered = [
            line for line in lines
            if not any(p.match(line.strip()) for p in _SUCCESS_PATTERNS)
        ]
        return '\n'.join(filtered)

    def _strip_timestamp_lines(self, text: str) -> str:
        """Remove lines that are exclusively timestamps."""
        lines = text.split('\n')
        filtered = []
        for line in lines:
            stripped = line.strip()
            # Only strip if the line IS a timestamp (not just contains one)
            if _TIMESTAMP_PATTERN.fullmatch(stripped):
                continue
            filtered.append(line)
        return '\n'.join(filtered)

    def _deduplicate_lines(self, text: str) -> str:
        """Remove consecutive duplicate lines."""
        lines = text.split('\n')
        if not lines:
            return text
        result = [lines[0]]
        for line in lines[1:]:
            if line != result[-1]:
                result.append(line)
        return '\n'.join(result)

    def _purify_structured(self, text: str, tool_name: str) -> str:
        """Try to detect and purify structured data (JSON)."""
        # Try to find JSON blocks
        text = self._purify_json_blocks(text, tool_name)
        
        # Try to find and compress JSON arrays
        text = self._compress_json_arrays(text)
        
        return text

    def _purify_json_blocks(self, text: str, tool_name: str) -> str:
        """Find JSON dicts and truncate them if they have too many keys."""
        def _truncate_json_dict(match):
            try:
                obj = json.loads(match.group(0))
                if isinstance(obj, dict):
                    keys = list(obj.keys())
                    if len(keys) > self.config.max_json_keys:
                        truncated = {k: obj[k] for k in keys[:self.config.max_json_keys]}
                        truncated[f"... ({len(keys) - self.config.max_json_keys} more keys)"] = "..."
                        return json.dumps(truncated, indent=2)
                return match.group(0)
            except (json.JSONDecodeError, ValueError):
                return match.group(0)
        
        # Match JSON objects
        return re.sub(
            r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}',
            _truncate_json_dict,
            text,
        )

    def _compress_json_arrays(self, text: str) -> str:
        """Compress long JSON arrays with identical structures."""
        def _compress_array(match):
            try:
                arr = json.loads(match.group(0))
                if isinstance(arr, list) and len(arr) > self.config.max_array_items:
                    return (
                        json.dumps(arr[:self.config.max_array_items], indent=2)
                        + f"\n  ... ({len(arr) - self.config.max_array_items} more items truncated)"
                    )
                return match.group(0)
            except (json.JSONDecodeError, ValueError):
                return match.group(0)
        
        # Match JSON arrays
        return re.sub(
            r'\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\]',
            _compress_array,
            text,
        )

    def stats(self, original: str, purified: str) -> dict:
        """Return compression stats for logging."""
        orig_len = len(original)
        new_len = len(purified)
        return {
            "original_chars": orig_len,
            "purified_chars": new_len,
            "compression_ratio": round(new_len / orig_len, 3) if orig_len > 0 else 1.0,
            "chars_saved": orig_len - new_len,
        }
