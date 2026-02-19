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

    public function getStockProductos(): array
    {
        return $this->buildSuccessResponse('stock-productos', 'stock.json');
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
