import os


class Settings:
    odoo_url: str = os.getenv("ODOO_URL", "http://localhost:8070")
    odoo_db: str = os.getenv("ODOO_DB", "pruebas-db")
    odoo_username: str = os.getenv("ODOO_USERNAME", "usuario_api")
    odoo_password: str = os.getenv("ODOO_PASSWORD", "1234")
    json_output_dir: str = os.getenv("JSON_OUTPUT_DIR", "generated_json")
    json_shopify_output_dir: str = os.getenv("JSON_SHOPIFY_OUTPUT_DIR", "json_shopify")
    shopify_store_url: str = os.getenv("SHOPIFY_STORE_URL", "")
    shopify_access_token: str = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
    shopify_api_version: str = os.getenv("SHOPIFY_API_VERSION", "2024-10")


settings = Settings()
