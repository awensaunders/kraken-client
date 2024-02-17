import asyncio
import logging
import os
from graphql_client import Client
from energy_api.kraken_rest_client import KrakenRestClient
import jwt
import datetime


async def main():
    logger = logging.getLogger("energy_api.main")
    endpoint = "https://api.eonnext-kraken.energy/v1/graphql/"
    anonymous_client = Client(endpoint)
    email = os.environ.get("KRAKEN_EMAIL", None)
    password = os.environ.get("KRAKEN_PASSWORD", None)
    api_key = os.environ.get("KRAKEN_API_KEY", None)

    if email is not None and password is not None:
        res = await anonymous_client.get_kraken_token_email_password(email, password)
        token = res.token
    elif api_key is not None:
        res = await anonymous_client.get_kraken_token_api_key(api_key)
        token = res.token
    else:
        raise Exception("No credentials found")

    logger.info("Logged In Successfully")
    logger.info(f"Token: {token}")
    token_decoded = jwt.decode(token, options={"verify_signature": False})
    exp = token_decoded["exp"]
    expiry = datetime.datetime.fromtimestamp(exp, tz=datetime.UTC)
    logger.info(f"Token Expiry: {expiry}")
    refresh_expiry = datetime.datetime.fromtimestamp(
        res.refresh_expires_in, tz=datetime.UTC
    )
    logger.info(f"Refresh Token Expiry: {refresh_expiry}")

    headers = {"Authorization": f"{token}"}
    authed_client = Client(endpoint, headers=headers)
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
    logger.info(f"Account Info: {res.model_dump_json()}")
    rc = KrakenRestClient("https://api.eonnext-kraken.energy/v1", headers)
    for account in accounts:
        gql_acc_details = await authed_client.account_agreement_and_meter_details(
            account.number
        )
        active_agreement = gql_acc_details.electricity_agreements[0]
        standing_charge = active_agreement.tariff.standing_charge
        mpan = active_agreement.meter_point.mpan
        msn = active_agreement.meter_point.meters[0].serial_number
        unit_rate = active_agreement.tariff.unit_rate
        logger.info(f"Getting account information for {account.number}")
        logger.info(f"Standing Charge: {standing_charge}")
        logger.info(f"Unit Rate: {unit_rate}")
        res = await rc.get_account_information(account.number)
        logger.info(f"Account Information: {res.model_dump_json()}")
        logger.info(f"Gathering consumption data for msn: {msn}")
        consumption = rc.get_consumption(mpan, msn, granularity="day")
        async for entry in consumption:
            logger.info(f"Consumption: {entry.model_dump_json()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
