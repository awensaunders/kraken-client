#!/usr/bin/env python3

import anyio
import logging
import logging.config
import os
from typing import Annotated

from energy_api.credentials import Credentials
from graphql_client import Client
from energy_api.kraken_rest_client import Granularity, KrakenRestClient
import jwt
from datetime import datetime, UTC, timedelta
import typer
from rich import print
from rich.console import Console
from rich.table import Table

app = typer.Typer()


@app.command()
def user_login(
    username: Annotated[str, typer.Option(prompt=True)],
    password: Annotated[str, typer.Option(prompt=True, hide_input=True)],
    endpoint: Annotated[str, typer.Option()] = "https://api.eonnext-kraken.energy",
):
    """
    Log into the api using a username (email) and password. Your username and
    password will not be saved, but a long-lived api key and tokens will be
    saved to disk.
    """
    try:
        creds = Credentials.load_from_disk()
        typer.confirm("Credentials already exist. Overwrite?", abort=True)
    except FileNotFoundError:
        pass
    creds = anyio.run(_user_login, username, password, endpoint)
    creds.save_to_disk()


async def _user_login(username: str, password: str, endpoint: str) -> Credentials:
    gql_endpoint = endpoint + "/v1/graphql/"
    client = Client(gql_endpoint)
    print(f"Logging in as {username}")
    res = await client.get_kraken_token_email_password(username, password)
    token = res.token
    token_decoded = jwt.decode(token, options={"verify_signature": False})
    token_expires_at = datetime.fromtimestamp(token_decoded["exp"], tz=UTC)
    refresh_expires_at = datetime.fromtimestamp(res.refresh_expires_in, tz=UTC)
    authed_client = Client(gql_endpoint, headers={"Authorization": f"{token}"})
    account_details = await authed_client.get_account_info()
    print(f"Logged in as {account_details.given_name} {account_details.family_name}")
    secret_key = await get_or_generate_secret_key(authed_client)

    return Credentials(
        secret_key=secret_key,
        endpoint=endpoint,
        token=token,
        token_expires_at=token_expires_at,
        refresh_token=res.refresh_token,
        refresh_expires_at=refresh_expires_at,
    )


async def get_or_generate_secret_key(client: Client) -> str:
    res = await client.get_account_info()
    if res.live_secret_key is not None:
        print("Using existing live secret key")
        return res.live_secret_key
    else:
        print("No live secret key found")
        print("Generating a new live secret key")
        res = await client.generate_secret_key()
        return res.live_secret_key


@app.command()
def api_key_login(
    api_key: Annotated[str, typer.Option(prompt=True, hide_input=True)],
    endpoint: Annotated[str, typer.Option()] = "https://api.eonnext-kraken.energy",
):
    """
    Log into the api using an API Key. This is not available through the UI for
    E.ON Next customers, but is available for Octopus Energy customers. The
    generated token will be saved to disk, along with your API key.
    """
    try:
        creds = Credentials.load_from_disk()
        typer.confirm("Credentials already exist. Overwrite?", abort=True)
    except FileNotFoundError:
        pass
    creds = anyio.run(_api_key_login, api_key, endpoint)
    creds.save_to_disk()


async def _api_key_login(api_key: str, endpoint: str) -> Credentials:
    gql_endpoint = endpoint + "/v1/graphql/"
    anonymous_client = Client(gql_endpoint)
    print("Logging in with API Key")
    res = await anonymous_client.get_kraken_token_api_key(api_key)
    token = res.token
    token_decoded = jwt.decode(token, options={"verify_signature": False})
    token_expires_at = datetime.fromtimestamp(token_decoded["exp"], tz=UTC)
    refresh_expires_at = datetime.fromtimestamp(res.refresh_expires_in, tz=UTC)
    authed_client = Client(gql_endpoint, headers={"Authorization": f"{token}"})
    account_details = await authed_client.get_account_info()
    print(f"Logged in as {account_details.given_name} {account_details.family_name}")
    # We obviously already have the API key, so we don't need to get it
    return Credentials(
        secret_key=api_key,
        endpoint=endpoint,
        token=token,
        token_expires_at=token_expires_at,
        refresh_token=res.refresh_token,
        refresh_expires_at=refresh_expires_at,
    )


@app.command()
def consumption(
    num: Annotated[int, typer.Argument(min=0, max=1000)],
    granularity: Annotated[
        Granularity, typer.Argument(case_sensitive=False)
    ] = Granularity.DAY,
):
    """
    Get consumption data for the last num periods (approximately, the data may
    not line up perfectly), where period is defined by the granularity.
    """
    creds = Credentials.load_from_disk()
    anyio.run(_consumption, creds, num, granularity)

async def _consumption(creds: Credentials, num: int, granularity: Granularity):
    rest_endpoint = creds.endpoint + "/v1"
    rc = KrakenRestClient(rest_endpoint, {"Authorization": f"{creds.token}"})
    gql_client = Client(creds.endpoint + "/v1/graphql/", headers={"Authorization": f"{creds.token}"})
    acc_info = await gql_client.get_account_info()
    for account in acc_info.accounts:
        print(f"Getting detailed account information for {account.number}")
        gql_acc_details = await gql_client.account_agreement_and_meter_details(
            account.number
        )
        active_agreement = gql_acc_details.electricity_agreements[0]
        standing_charge = active_agreement.tariff.standing_charge
        mpan = active_agreement.meter_point.mpan
        msn = active_agreement.meter_point.meters[0].serial_number
        unit_rate = active_agreement.tariff.unit_rate
        print(f"Current Standing Charge: {standing_charge}")
        print(f"Current Unit Rate: {unit_rate}")
        if granularity == Granularity.HALFHOUR:
            period_from = datetime.now(tz=UTC) - (timedelta(minutes=30) * num)
        elif granularity == Granularity.HOUR:
            period_from = datetime.now(tz=UTC) - (timedelta(hours=1) * num)
        elif granularity == Granularity.DAY:
            period_from = datetime.now(tz=UTC) - (timedelta(days=1) * num)
        elif granularity == Granularity.MONTH:
            period_from = datetime.now(tz=UTC) - (timedelta(days=30) * num)
        else:
            raise ValueError(f"Unknown granularity: {granularity}")
        consumption_data =rc.get_consumption(mpan, msn, granularity=granularity, period_from=period_from)

        table = Table(title="Consumption Data")
        table.add_column("Period Start")
        table.add_column("Period End")
        table.add_column("Consumption (kWh)")
        async for entry in consumption_data:
            table.add_row(str(entry.interval_start), str(entry.interval_end), str(entry.consumption))
        console = Console()
        console.print(table)
        typer.Exit()



if __name__ == "__main__":
    app()
