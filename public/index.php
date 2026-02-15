<?php

declare(strict_types=1);

use App\Core\JsonResponse;

require __DIR__ . '/../bootstrap/app.php';

$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
$uri = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';

$response = $router->dispatch($method, $uri);

if ($response === null) {
    JsonResponse::send([
        'ok' => false,
        'message' => 'Endpoint no encontrado',
        'status' => 404,
    ], 404);
    exit;
}

JsonResponse::send($response['body'], $response['status']);
