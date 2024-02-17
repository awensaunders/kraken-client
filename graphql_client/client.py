# Generated by ariadne-codegen
# Source: gql/

from typing import Any, Dict, Optional, Union

from .account_agreement_and_meter_details import (
    AccountAgreementAndMeterDetails,
    AccountAgreementAndMeterDetailsAccount,
)
from .async_base_client import AsyncBaseClient
from .base_model import UNSET, UnsetType
from .generate_secret_key import GenerateSecretKey, GenerateSecretKeyRegenerateSecretKey
from .get_account_info import GetAccountInfo, GetAccountInfoViewer
from .get_kraken_token_api_key import (
    GetKrakenTokenAPIKey,
    GetKrakenTokenAPIKeyObtainKrakenToken,
)
from .get_kraken_token_email_password import (
    GetKrakenTokenEmailPassword,
    GetKrakenTokenEmailPasswordObtainKrakenToken,
)


def gql(q: str) -> str:
    return q


class Client(AsyncBaseClient):
    async def account_agreement_and_meter_details(
        self, account: str, **kwargs: Any
    ) -> Optional[AccountAgreementAndMeterDetailsAccount]:
        query = gql(
            """
            query accountAgreementAndMeterDetails($account: String!) {
              account(accountNumber: $account) {
                electricityAgreements(active: true) {
                  id
                  validTo
                  validFrom
                  tariff {
                    __typename
                    ... on StandardTariff {
                      id
                      productCode
                      standingCharge
                      unitRate
                    }
                    ... on TariffType {
                      id
                      productCode
                      standingCharge
                    }
                  }
                  meterPoint {
                    id
                    mpan
                    status
                    meters(includeInactive: false) {
                      serialNumber
                      smartDevices {
                        id
                        deviceId
                        serialNumber
                      }
                    }
                  }
                }
                campaigns {
                  name
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"account": account}
        response = await self.execute(
            query=query,
            operation_name="accountAgreementAndMeterDetails",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return AccountAgreementAndMeterDetails.model_validate(data).account

    async def generate_secret_key(
        self, **kwargs: Any
    ) -> Optional[GenerateSecretKeyRegenerateSecretKey]:
        query = gql(
            """
            mutation generateSecretKey {
              regenerateSecretKey {
                viewer {
                  liveSecretKey
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {}
        response = await self.execute(
            query=query,
            operation_name="generateSecretKey",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return GenerateSecretKey.model_validate(data).regenerate_secret_key

    async def get_account_info(self, **kwargs: Any) -> Optional[GetAccountInfoViewer]:
        query = gql(
            """
            query getAccountInfo {
              viewer {
                givenName
                familyName
                email
                liveSecretKey
                accounts(restrictToPublicFacingBrands: false) {
                  __typename
                  number
                  status
                  balance
                  brand
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {}
        response = await self.execute(
            query=query, operation_name="getAccountInfo", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return GetAccountInfo.model_validate(data).viewer

    async def get_kraken_token_api_key(
        self, api_key: str, **kwargs: Any
    ) -> Optional[GetKrakenTokenAPIKeyObtainKrakenToken]:
        query = gql(
            """
            mutation getKrakenTokenAPIKey($APIKey: String!) {
              obtainKrakenToken(input: {APIKey: $APIKey}) {
                token
                refreshToken
                refreshExpiresIn
              }
            }
            """
        )
        variables: Dict[str, object] = {"APIKey": api_key}
        response = await self.execute(
            query=query,
            operation_name="getKrakenTokenAPIKey",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return GetKrakenTokenAPIKey.model_validate(data).obtain_kraken_token

    async def get_kraken_token_email_password(
        self,
        email: Union[Optional[str], UnsetType] = UNSET,
        password: Union[Optional[str], UnsetType] = UNSET,
        **kwargs: Any
    ) -> Optional[GetKrakenTokenEmailPasswordObtainKrakenToken]:
        query = gql(
            """
            mutation getKrakenTokenEmailPassword($email: String, $password: String) {
              obtainKrakenToken(input: {email: $email, password: $password}) {
                token
                refreshToken
                refreshExpiresIn
              }
            }
            """
        )
        variables: Dict[str, object] = {"email": email, "password": password}
        response = await self.execute(
            query=query,
            operation_name="getKrakenTokenEmailPassword",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return GetKrakenTokenEmailPassword.model_validate(data).obtain_kraken_token
