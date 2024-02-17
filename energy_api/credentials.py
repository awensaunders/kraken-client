import typer
from rich import print
import os
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
from energy_api import APP_NAME

class Credentials(BaseModel):
    secret_key: str
    endpoint: str
    token: str
    token_expires_at: datetime
    refresh_token: str
    refresh_expires_at: datetime

    def save_to_disk(self):
        config_path = typer.get_app_dir(APP_NAME)
        if not os.path.exists(config_path):
            print(f"Creating config directory: {config_path}")
            os.makedirs(config_path)
        config_file = Path(config_path) / "config.json"
        with open(config_file, "w") as f:
            print(f"Writing credentials to {config_file}")
            f.write(self.model_dump_json())
    
    @classmethod
    def load_from_disk(cls):
        config_path = typer.get_app_dir(APP_NAME)
        config_file = Path(config_path) / "config.json"
        with open(config_file, "r") as f:
            print(f"Reading credentials from {config_file}")
            return cls.model_validate_json(f.read())