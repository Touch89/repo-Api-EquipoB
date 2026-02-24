<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Services\DataService;
use App\Services\PrestashopService;
use App\Services\OdooService;
use RuntimeException;

final class ApiController
{
    public function __construct(private DataService $dataService)
    {
    }

    public function getProductos(): array
    {
        return $this->buildSuccessResponse('productos', 'products.json');
    }

    public function getOrdenes(): array
    {
        return $this->buildSuccessResponse('ordenes', 'orders.json');
    }

    public function getCategorias2(): array
    {
        return $this->buildSuccessResponse('categorias', 'categories.json');
    }

    public function getCategorias(): array
    {
        $data = [
            ['id' => 1, 'nombre' => 'Electrónica'],
            ['id' => 2, 'nombre' => 'Ropa'],
        ];

        return [
            'status' => 200,
            'body' => [
                'ok' => true,
                'endpoint' => 'categorias',
                'count' => count($data),
                'data' => $data,
            ],
        ];
    }

    public function getStockProductos(): array
    {
        return $this->buildSuccessResponse('stock-productos', 'stock.json');
    }

    public function getProveedores(): array
    {
        return $this->buildSuccessResponse('proveedores', 'providers.json');
    }

    public function getPrestashopPagos(): array
    {
        try {
            $service = new PrestashopService();
            $pagos = $service->getPagos();

            return [
                'status' => 200,
                'body' => [
                    'status' => 'success',
                    'data' => $pagos,
                    'errors' => [],
                ],
            ];
        } catch (\Throwable $e) {
            return [
                'status' => 400,
                'body' => [
                    'status' => 'error',
                    'data' => null,
                    'errors' => [
                        [
                            'code' => '400',
                            'message' => $e->getMessage(),
                        ],
                    ],
                ],
            ];
        }
    }

    public function getPrestashopClientes(): array
    {
        return $this->buildPrestashopResponse('prestashop_clients.json');
    }

    public function getPrestashopProveedores(): array
    {
        return $this->buildPrestashopResponse('prestashop_providers.json');
    }

    public function getOdooPagos(): array
    {
        try {
            $service = new OdooService();
            $pagos = $service->getPagos();

            return [
                'status' => 200,
                'body' => [
                    'status' => 'success',
                    'data' => $pagos,
                    'errors' => [],
                ],
            ];
        } catch (\Throwable $e) {
            return [
                'status' => 400,
                'body' => [
                    'status' => 'error',
                    'data' => null,
                    'errors' => [
                        [
                            'code' => '400',
                            'message' => $e->getMessage(),
                        ],
                    ],
                ],
            ];
        }
    }

    private function buildSuccessResponse(string $endpoint, string $fileName): array
    {
        try {
            $data = $this->dataService->getCollection($fileName);

            return [
                'status' => 200,
                'body' => [
                    'ok' => true,
                    'endpoint' => $endpoint,
                    'count' => count($data),
                    'data' => $data,
                ],
            ];
        } catch (RuntimeException $exception) {
            return [
                'status' => 500,
                'body' => [
                    'ok' => false,
                    'message' => $exception->getMessage(),
                ],
            ];
        }
    }

    private function buildPrestashopResponse(string $fileName): array
    {
        try {
            $data = $this->dataService->getCollection($fileName);

            return [
                'status' => 200,
                'body' => [
                    'status' => 'success',
                    'data' => $data,
                    'errors' => [],
                ],
            ];
        } catch (RuntimeException $exception) {
            return [
                'status' => 400,
                'body' => [
                    'status' => 'error',
                    'data' => null,
                    'errors' => [
                        [
                            'code' => '400',
                            'message' => $exception->getMessage(),
                        ],
                    ],
                ],
            ];
        }
    }
}
