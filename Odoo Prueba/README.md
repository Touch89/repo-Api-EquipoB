# Odoo API (Python + FastAPI)

## Ejecutar

```powershell
py -m uvicorn main:app --reload --port 8090
```

## Ejecutar con Docker Compose

```powershell
docker compose up -d --build api
```

Si también quieres levantar Odoo + DB + API:

```powershell
docker compose up -d --build
```

Si también quieres levantar PrestaShop + MariaDB:

```powershell
docker compose up -d --build prestashop prestashop-db
```

Base URL local:

- `http://127.0.0.1:8090`
- `http://127.0.0.1:8091` (Docker Compose)
- `http://127.0.0.1:8081` (PrestaShop en Docker Compose)

## Variables de conexión a Odoo

- `ODOO_URL` (default: `http://localhost:8070`)
- `ODOO_DB` (default: `pruebas-db`)
- `ODOO_USERNAME` (default: `usuario_api`)
- `ODOO_PASSWORD` (default: `1234`)
- `JSON_OUTPUT_DIR` (default: `generated_json`)

## Variables de conexión a PrestaShop

- `PRESTASHOP_URL` (ejemplo: `http://localhost:8081` o `http://prestashop` en Docker)
- `PRESTASHOP_API_KEY` (Webservice key)
- `PRESTASHOP_LANGUAGE_ID` (default: `1`)
- `PRESTASHOP_HOST_HEADER` (default: `localhost:8081`)
- `JSON_PRESTASHOP_OUTPUT_DIR` (default: `json_prestashop`)

En PowerShell:

```powershell
$env:ODOO_URL="http://localhost:8070"
$env:ODOO_DB="pruebas-db"
$env:ODOO_USERNAME="usuario_api"
$env:ODOO_PASSWORD="1234"
$env:JSON_OUTPUT_DIR="generated_json"
```

## Generación de JSON por consulta

Cada consulta a endpoint genera automáticamente un archivo `.json` con:

- método y ruta de la request
- query params
- body de request
- status code y body de response

Por defecto se guardan en la carpeta `generated_json/`.

Las consultas a endpoints de PrestaShop se guardan en `json_prestashop/`.

La nomenclatura es por endpoint y número incremental, por ejemplo:

- `ordenes_1.json`, `ordenes_2.json`
- `productos_1.json`, `productos_2.json`
- `stock_productos_1.json`
- `categorias_productos_1.json`

Si ejecutas con Docker Compose, la carpeta `generated_json/` del proyecto queda montada en el contenedor (`/app/generated_json`), así que los archivos se ven directamente en tu proyecto.

## Endpoints

- `GET /health`
- `GET /api/orders`
- `GET /api/products`
- `GET /api/products/stock`
- `GET /api/products/categories`
- `GET /api/customers`
- `GET /api/suppliers`
- `GET /api/payments`
- `GET /api/products/by-sku/{sku}`
- `GET /api/orders/by-reference/{reference}`
- `GET /api/sync/products`
- `GET /api/sync/products/by-reference/{reference}`
- `GET /api/sync/products/update/by-reference/{reference}`
- `GET /api/sync/products/deactivate/by-reference/{reference}`
- `POST /api/products`
- `POST /api/products/bulk`
- `GET /api/prestashop/products`
- `GET /api/prestashop/orders`
- `GET /api/prestashop/customers`
- `GET /api/prestashop/suppliers`
- `GET /api/prestashop/payments`
- `GET /api/prestashop/products/by-sku/{sku}`
- `GET /api/prestashop/orders/by-reference/{reference}`

> Nota: `POST /api/products` y `POST /api/products/bulk` ahora crean el producto en **Odoo y PrestaShop**. Si falla PrestaShop, la API revierte la creación hecha en Odoo dentro de esa misma petición para evitar desincronización.

## Comandos de terminal para cada request

Usa una base URL según cómo ejecutes la API:

```powershell
$base = "http://127.0.0.1:8090"  # local
# $base = "http://127.0.0.1:8091"  # docker
```

### GET

```powershell
Invoke-RestMethod -Method Get -Uri "$base/health"
Invoke-RestMethod -Method Get -Uri "$base/api/orders"
Invoke-RestMethod -Method Get -Uri "$base/api/products"
Invoke-RestMethod -Method Get -Uri "$base/api/products/stock"
Invoke-RestMethod -Method Get -Uri "$base/api/products/categories"
Invoke-RestMethod -Method Get -Uri "$base/api/customers"
Invoke-RestMethod -Method Get -Uri "$base/api/suppliers"
Invoke-RestMethod -Method Get -Uri "$base/api/payments"
Invoke-RestMethod -Method Get -Uri "$base/api/products/by-sku/SKU-DEMO-001"
Invoke-RestMethod -Method Get -Uri "$base/api/orders/by-reference/S00001"
Invoke-RestMethod -Method Get -Uri "$base/api/sync/products?limit=200"
Invoke-RestMethod -Method Get -Uri "$base/api/sync/products/by-reference/FURN_7777"
Invoke-RestMethod -Method Get -Uri "$base/api/sync/products/update/by-reference/FURN_7777"
Invoke-RestMethod -Method Get -Uri "$base/api/sync/products/deactivate/by-reference/FURN_7777"
Invoke-RestMethod -Method Get -Uri "$base/api/prestashop/products"
Invoke-RestMethod -Method Get -Uri "$base/api/prestashop/orders"
Invoke-RestMethod -Method Get -Uri "$base/api/prestashop/customers"
Invoke-RestMethod -Method Get -Uri "$base/api/prestashop/suppliers"
Invoke-RestMethod -Method Get -Uri "$base/api/prestashop/payments"
Invoke-RestMethod -Method Get -Uri "$base/api/prestashop/products/by-sku/FURN_7777"
Invoke-RestMethod -Method Get -Uri "$base/api/prestashop/orders/by-reference/REF-TEST"
```

### POST /api/products

```powershell
$body = @{
  name = "Producto Demo"
  list_price = 120.0
  standard_price = 80.0
  default_code = "SKU-DEMO-001"
  categ_id = 1
  type = "consu"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$base/api/products" -ContentType "application/json" -Body $body
```

### POST /api/products/bulk

```powershell
$body = @{
  products = @(
    @{
      name = "Producto A"
      list_price = 100.0
      standard_price = 60.0
      default_code = "SKU-A"
      categ_id = 1
      type = "consu"
    },
    @{
      name = "Producto B"
      list_price = 150.0
      standard_price = 90.0
      default_code = "SKU-B"
      categ_id = 1
      type = "consu"
    }
  )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri "$base/api/products/bulk" -ContentType "application/json" -Body $body
```

### Alternativa con curl

```bash
curl "$base/health"
curl "$base/api/orders"
curl "$base/api/products"
curl "$base/api/products/stock"
curl "$base/api/products/categories"

curl -X POST "$base/api/products" \
  -H "Content-Type: application/json" \
  -d '{"name":"Producto Demo","list_price":120.0,"standard_price":80.0,"default_code":"SKU-DEMO-001","categ_id":1,"type":"consu"}'

curl -X POST "$base/api/products/bulk" \
  -H "Content-Type: application/json" \
  -d '{"products":[{"name":"Producto A","list_price":100.0,"standard_price":60.0,"default_code":"SKU-A","categ_id":1,"type":"consu"},{"name":"Producto B","list_price":150.0,"standard_price":90.0,"default_code":"SKU-B","categ_id":1,"type":"consu"}]}'
```

## Crear producto

`POST /api/products`

```json
{
  "name": "Producto Demo",
  "list_price": 120.0,
  "standard_price": 80.0,
  "default_code": "SKU-DEMO-001",
  "categ_id": 1,
  "type": "consu"
}
```

## Creación masiva

`POST /api/products/bulk`

```json
{
  "products": [
    {
      "name": "Producto A",
      "list_price": 100.0,
      "standard_price": 60.0,
      "default_code": "SKU-A",
      "categ_id": 1,
      "type": "consu"
    },
    {
      "name": "Producto B",
      "list_price": 150.0,
      "standard_price": 90.0,
      "default_code": "SKU-B",
      "categ_id": 1,
      "type": "consu"
    }
  ]
}
```
