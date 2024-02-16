from datetime import datetime
import httpx
import logging
from pydantic import BaseModel
from rest_api_models.account_models import AccountInformation


logger = logging.getLogger(__name__)
class KrakenRestClient:
    def __init__(self, endpoint, auth_headers):
        self.endpoint = endpoint
        # self.auth_headers = auth_headers
        self.client = httpx.AsyncClient(headers=auth_headers)
    
    async def get_account_information(self, account_number: str) -> AccountInformation:
        res = await self.client.get(f"{self.endpoint}/accounts/{account_number}/")
        logger.info(f"Called get_account_information, got:{res}")
        res.raise_for_status()
        return AccountInformation.model_validate_json(res.text)


