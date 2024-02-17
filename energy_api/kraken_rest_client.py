from datetime import datetime, timedelta, UTC
from typing import AsyncIterator, Literal
import httpx
import logging
from rest_api_models.account_models import AccountInformation
from rest_api_models.consumption_models import ConsumptionEntry, PaginatedConsumption


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

    async def get_consumption(
        self,
        mpan: str,
        msn: str,
        granularity: Literal["halfhour", "hour", "day", "month"],
        period_from: datetime = (datetime.now(tz=UTC) - timedelta(days=7)),
        period_to: datetime = datetime.now(tz=UTC),
    ) -> AsyncIterator[ConsumptionEntry]:
        group_by = granularity
        params = {
            "order_by": "-period",
            "group_by": group_by,
            "period_from": period_from.isoformat(),
            "period_to": period_to.isoformat(),
        }
        if group_by == "halfhour":
            # halfhour is the default, and the API doesn't like it being set explicitly
            del params["group_by"]

        res = await self.client.get(
            f"{self.endpoint}/electricity-meter-points/{mpan}/meters/{msn}/consumption/",
            timeout=10,
            params=params,
        )
        logger.info(f"Called get_consumption, got:{res}")
        res.raise_for_status()
        paginated = PaginatedConsumption.model_validate_json(res.text)
        page = 1
        for entry in paginated.results:
            yield entry
        while paginated.next is not None:
            page += 1
            res = await self.client.get(paginated.next)
            logger.info(f"Called get_consumption on page {page}, got:{res}")
            res.raise_for_status()
            paginated = PaginatedConsumption.model_validate_json(res.text)
            for entry in paginated.results:
                yield entry
