from functools import cache
from gql import gql, Client
from gql.transport.httpx import HTTPXAsyncTransport
import pathlib

GQL_FOLDER = str(pathlib.Path(__file__).parent) + "/gql"
class GqlFileHandler:
    def __init__(
        self, client: Client, base_path: str = str(pathlib.Path(__file__).parent) + "/gql"
    ):
        self.client = client
        self.base_path = base_path
        return

    @cache
    def gql(self, file_name: str):
        with open(f"{self.base_path}/{file_name}", "r") as file:
            return gql(file.read())


class KrakenGqlClient:
    def __init__(self, endpoint: str, email: str, password: str):
        self.email = email
        self.password = password
        transport = HTTPXAsyncTransport(url=endpoint)
        schema = None
        with open(GQL_FOLDER + "/schema.gql", "r") as file:
            schema = file.read()
        self.client = Client(transport=transport, schema=schema)
        self.fh = GqlFileHandler(self.client)
        self._getKrakenTokenWithEmailPass()

    def _getKrakenTokenWithEmailPass(self):
        params = {"email": self.email, "password": self.password}
        m = self.fh.gql("getToken.gql")
        res = self.client.execute(m, variable_values=params)
        self.token = res["obtainKrakenToken"]["token"]
        self.refresh_token = res["obtainKrakenToken"]["refreshToken"]
        self.refresh_expires_in = res["obtainKrakenToken"]["refreshExpiresIn"]
        return
