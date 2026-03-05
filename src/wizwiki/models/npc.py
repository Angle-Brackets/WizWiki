from __future__ import annotations
from typing import Optional
from .base import Resource, View


class NPCView(View):
    """View of an NPC resource."""


class NPC(Resource):
    """Represents an NPC in Wizard101."""
    category: str = "NPC"

    @classmethod
    async def get(cls, name: str, client: Optional['WizWikiClient'] = None) -> 'NPC':
        """Fetch an NPC by name."""
        if client is None:
            from .. import _default_client
            client = _default_client
        return await client.get_resource(name, "NPC")

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> 'NPC':
        raise NotImplementedError("Parsing for NPC is not yet implemented.")
