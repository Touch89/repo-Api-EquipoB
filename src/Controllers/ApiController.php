<?php

declare(strict_types=1);

namespace App\Controllers;

use App\Services\DataService;
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

    // ✅ NUEVO: endpoint categorías (mismo formato que productos)
    public function getCategorias(): array
    {
        // Opción A (recomendada): si vas a usar archivo JSON como productos
        // return $this->buildSuccessResponse('categorias', 'categories.json');

        // Opción B: mock directo (como lo estabas haciendo)
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
}
