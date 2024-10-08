# Generated by ariadne-codegen
# Source: gql/

from typing import List, Literal, Optional

from pydantic import Field

from .base_model import BaseModel
from .enums import AccountStatus


class GetAccountInfo(BaseModel):
    viewer: Optional["GetAccountInfoViewer"]


class GetAccountInfoViewer(BaseModel):
    given_name: str = Field(alias="givenName")
    family_name: str = Field(alias="familyName")
    email: str
    live_secret_key: Optional[str] = Field(alias="liveSecretKey")
    accounts: Optional[List[Optional["GetAccountInfoViewerAccounts"]]]


class GetAccountInfoViewerAccounts(BaseModel):
    typename__: Literal["AccountInterface", "AccountType"] = Field(alias="__typename")
    number: Optional[str]
    status: Optional[AccountStatus]
    balance: int
    brand: Optional[str]
