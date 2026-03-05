from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Resource, View

if TYPE_CHECKING:
    from ..client import WizWikiClient


class JewelView(View):
    category: str = "Jewel"


class Jewel(Resource):
    category: str = "Jewel"

    @classmethod
    async def get(cls, name: str, client: Optional['WizWikiClient'] = None) -> 'Jewel':
        """
        Public method to fetch a Jewel by name.
        """
        if client is None:
            from .. import _default_client
            client = _default_client
        return await client.get_resource(name, "Jewel")

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> Jewel:
        raise NotImplementedError("Parsing for Jewel is not yet implemented.")
