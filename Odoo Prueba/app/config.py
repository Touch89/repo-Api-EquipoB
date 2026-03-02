import os


class Settings:
    odoo_url: str = os.getenv("ODOO_URL", "http://localhost:8070")
    odoo_db: str = os.getenv("ODOO_DB", "pruebas-db")
    odoo_username: str = os.getenv("ODOO_USERNAME", "usuario_api")
    odoo_password: str = os.getenv("ODOO_PASSWORD", "1234")
    json_output_dir: str = os.getenv("JSON_OUTPUT_DIR", "generated_json")
    json_prestashop_output_dir: str = os.getenv("JSON_PRESTASHOP_OUTPUT_DIR", "json_prestashop")
    prestashop_url: str = os.getenv("PRESTASHOP_URL", "http://prestashop")
    prestashop_api_key: str = os.getenv("PRESTASHOP_API_KEY", "")
    prestashop_language_id: int = int(os.getenv("PRESTASHOP_LANGUAGE_ID", "1"))
    prestashop_host_header: str = os.getenv("PRESTASHOP_HOST_HEADER", "localhost:8081")


settings = Settings()
