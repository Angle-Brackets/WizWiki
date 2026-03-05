from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, PrivateAttr

if TYPE_CHECKING:
    from ..client import WizWikiClient


class View(BaseModel):
    """
    A thin wrapper for a wiki resource.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    category: str
    url: str
    _client: WizWikiClient = PrivateAttr(default=None)

    async def get(self) -> Resource:
        """
        Fetches the full resource data.
        """
        if not self._client:
            raise ValueError("Client not initialized for this View.")
        return await self._client.get_resource(self.name, self.category)


class Resource(BaseModel):
    """
    The full data variant of a wiki resource.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    category: str
    url: str
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> 'Resource':
        """
        Parses HTML content into a Resource object.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _parse() logic.")
