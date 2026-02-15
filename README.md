# API Equipo B (PHP)

API monolítica modular en PHP con endpoints que responden JSON.

## Ejecutar local

Desde la raíz del repositorio:

```bash
php -S localhost:8000 -t public
```

## Endpoint

- `GET /api/productos`

Todos devuelven una estructura JSON tipo:

```json
{
  "ok": true,
  "endpoint": "productos",
  "count": 2,
  "data": []
}
```
