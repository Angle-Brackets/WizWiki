from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Resource, View

if TYPE_CHECKING:
    from ..client import WizWikiClient


class ReagentView(View):
    category: str = "Reagent"


class Reagent(Resource):
    category: str = "Reagent"

    @classmethod
    async def get(cls, name: str, client: Optional['WizWikiClient'] = None) -> 'Reagent':
        """
        Public method to fetch a Reagent by name.
        """
        if client is None:
            from .. import _default_client
            client = _default_client
        return await client.get_resource(name, "Reagent")

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> Reagent:
        raise NotImplementedError("Parsing for Reagent is not yet implemented.")
