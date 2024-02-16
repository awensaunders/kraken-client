import logging
from energy_api.gql_client import KrakenGqlClient
import os

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    email = os.environ.get('KRAKEN_EMAIL')
    password = os.environ.get('KRAKEN_PASSWORD')
    endpoint = "https://api.eonnext-kraken.energy/v1/graphql/"
    c = KrakenGqlClient(endpoint, email, password)
    logger.info("Logged into Kraken API")
    logger.info(f"Token: {c.token}")