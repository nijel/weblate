# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Metadata for terminology alternatives stored alongside multivalue strings."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

from translate.storage.tbx import match_term_indices

from weblate.trans.util import split_plural

if TYPE_CHECKING:
    from weblate.trans.models import Unit


def reconcile_terms(records: list[dict], texts: list[str]) -> list[dict]:
    """Use the same occurrence/text matching as the TBX writer."""
    matches = match_term_indices([record["text"] for record in records], texts)
    result = []
    for text, index in zip(texts, matches, strict=True):
        record = (
            deepcopy(records[index])
            if index is not None
            else {
                "id": None,
                "administrative_status": None,
                "notes": [],
            }
        )
        record["text"] = text
        result.append(record)
    return result


def term_records(unit: Unit, *, source: bool = False) -> list[dict[str, Any]]:
    """Return records aligned with current, possibly uncommitted string values."""
    side = "source" if source else "target"
    texts = split_plural(unit.source if source else unit.target)
    records = unit.details.get("tbx_terms", {}).get(side, [])
    if not records and not any(texts):
        return []
    return reconcile_terms(records, texts)


def term_forbidden(record: dict) -> bool:
    return (record.get("administrative_status") or "").strip().lower() in {
        "forbidden",
        "obsolete",
        "deprecated",
        "deprecatedtermadmnsts",
        "deprecatedterm-admn-sts",  # codespell:ignore
    }
