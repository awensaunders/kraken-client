import asyncio
import logging
import os
from graphql_client import Client
from kraken_rest_client import KrakenRestClient

logger = logging.getLogger(__name__)

async def main():
    c = Client("https://api.eonnext-kraken.energy/v1/graphql/")
    email = os.environ.get("KRAKEN_EMAIL")
    password = os.environ.get("KRAKEN_PASSWORD")
    res = await c.get_kraken_token(email, password)
    token = res.token
    logger.info("Logged In Successfully")
    logger.info(f"Token: {token}")
    headers = {
        "Authorization": f"{token}"
    }
    authed_client = Client("https://api.eonnext-kraken.energy/v1/graphql/", headers=headers)
    res = await authed_client.get_account_info()
    logger.info(f"Logged in as {res.family_name} {res.given_name}")
    if res.live_secret_key is not None:
        logger.info(f"Live Secret Key: {res.live_secret_key}")
    else:
        logger.info("No live secret key found")
        logger.info("Creating a new live secret key")
        res = await authed_client.generate_secret_key()
        logger.info(f"Generated new secret key: {res.live_secret_key}")
    res = await authed_client.get_account_info()
    accounts = res.accounts
    sk = res.live_secret_key
    logger.info(f"Account Info: {res.model_dump_json()}")
    rc = KrakenRestClient("https://api.eonnext-kraken.energy/v1", headers)
    for account in accounts:
        gql_acc_details = await authed_client.account_agreement_and_meter_details(account.number)
        active_agreement = gql_acc_details.electricity_agreements[0]
        standing_charge = active_agreement.tariff.standing_charge
        unit_rate = active_agreement.tariff.unit_rate
        logger.info(f"Getting account information for {account.number}")
        logger.info(f"Standing Charge: {standing_charge}")
        logger.info(f"Unit Rate: {unit_rate}")
        res = await rc.get_account_information(account.number)
        logger.info(f"Account Information: {res.model_dump_json()}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())