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

Base URL local:

- `http://127.0.0.1:8090`
- `http://127.0.0.1:8091` (Docker Compose)

## Variables de conexión a Odoo

- `ODOO_URL` (default: `http://localhost:8070`)
- `ODOO_DB` (default: `pruebas-db`)
- `ODOO_USERNAME` (default: `usuario_api`)
- `ODOO_PASSWORD` (default: `1234`)
- `JSON_OUTPUT_DIR` (default: `generated_json`)

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
- `POST /api/products`
- `POST /api/products/bulk`

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
