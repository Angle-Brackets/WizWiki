from __future__ import annotations
from typing import Optional
from .base import Resource, View


class QuestView(View):
    """View of a Quest resource."""


class Quest(Resource):
    """Represents a Quest in Wizard101."""
    category: str = "Quest"

    @classmethod
    async def get(cls, name: str, client: Optional['WizWikiClient'] = None) -> 'Quest':
        """Fetch a Quest by name."""
        if client is None:
            from .. import _default_client
            client = _default_client
        return await client.get_resource(name, "Quest")

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> 'Quest':
        raise NotImplementedError("Parsing for Quest is not yet implemented.")
