"""
Output Polish Layer

Cleans repeated wording, casing issues, and obvious presentation problems
before client-facing delivery.
"""

from typing import Dict, Any
import copy
import re


class OutputPolishLayer:
    def polish_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        polished = copy.deepcopy(output)
        return self._polish_value(polished)

    def _polish_value(self, value):
        if isinstance(value, dict):
            return {key: self._polish_value(item) for key, item in value.items()}

        if isinstance(value, list):
            return [self._polish_value(item) for item in value]

        if isinstance(value, str):
            return self._clean_text(value)

        return value

    def _clean_text(self, text: str) -> str:
        cleaned = text

        replacements = {
            "accent accent": "accent",
            "natural, premium, trustworthy, emotionally believable, natural, emotionally believable": "natural, premium, trustworthy, emotionally believable",
            "premium ecommerce product image image": "premium ecommerce product image",
            "direction..": "direction.",
            "United arab emirates": "United Arab Emirates",
            "united arab emirates": "United Arab Emirates",
        }

        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)

        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned


def polish_summary(output: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "client_safe": output.get("client_safe"),
        "output_type": output.get("output_type"),
        "product_name": output.get("product_name"),
        "content": output.get("content"),
    }