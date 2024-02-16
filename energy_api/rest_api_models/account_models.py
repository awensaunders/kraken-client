from datetime import datetime
from pydantic import BaseModel

class Agreement(BaseModel):
    tariff_code: str
    valid_from: datetime
    valid_to: datetime | None

class Register(BaseModel):
    identifier: str
    rate: str
    is_settlement_register: bool

class Meter(BaseModel):
    serial_number: str
    registers: list[Register]

class ElectricityMeterPoint(BaseModel):
    mpan: str
    profile_class: int
    consumption_standard: int
    meters: list[Meter]
    agreements: list[Agreement]
    is_export: bool

class PropertyInformation(BaseModel):
    id: int
    moved_in_at: datetime | None
    moved_out_at: datetime | None
    address_line_1: str
    address_line_2: str
    address_line_3: str
    town: str
    county: str
    postcode: str
    electricity_meter_points: list[ElectricityMeterPoint]

class AccountInformation(BaseModel):
    number: str
    properties: list[PropertyInformation]