<?php

declare(strict_types=1);

namespace App\Core;

final class JsonResponse
{
    public static function send(array $body, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($body, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    }
}
