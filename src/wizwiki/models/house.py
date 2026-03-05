from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Resource, View

if TYPE_CHECKING:
    from ..client import WizWikiClient


class HouseView(View):
    category: str = "House"


class House(Resource):
    category: str = "House"

    @classmethod
    async def get(cls, name: str, client: Optional['WizWikiClient'] = None) -> 'House':
        """
        Public method to fetch a House by name.
        """
        if client is None:
            from .. import _default_client
            client = _default_client
        return await client.get_resource(name, "House")

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> House:
        raise NotImplementedError("Parsing for House is not yet implemented.")
