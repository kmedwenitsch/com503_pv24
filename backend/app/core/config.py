from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "PV24 Forecast Prototype"
    app_tz: str = "Europe/Vienna"

    lat: float = 47.797777777778
    lon: float = 16.296666666667

    pv_csv_path: str = "./input_data/production.csv"
    pv_value_column: str = "AT0090000000000000000X312X009800E"
    pv_capacity_kw: float = 5.0

    entsoe_api_key: str | None = None
    entsoe_bidding_zone: str = "10YAT-APG------L"


settings = Settings()
