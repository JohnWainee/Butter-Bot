"""Doc plans: the contract between generators, drafters, and the writer."""

from typing import Any

from pydantic import BaseModel


class SectionPlan(BaseModel):
    """One planned managed section.

    `generated` holds deterministic, ready-to-install markdown. `brief`
    asks the drafter (the driving session, or litellm later) to improve
    or extend it. The writer validates whatever comes back.
    """

    name: str
    facts: dict[str, Any]
    facts_hash: str
    generated: str
    brief: str | None = None


class DocPlan(BaseModel):
    """A full document plan for one doc type."""

    doc_type: str
    title: str
    target_path: str
    sections: list[SectionPlan]
