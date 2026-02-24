<?php

declare(strict_types=1);

namespace App\Services;

use RuntimeException;

final class OdooService
{
    private string $baseUrl;

    public function __construct()
    {
        $this->baseUrl = 'http://localhost:8069/api';
    }

    public function getPagos(): array
    {
        $url = $this->baseUrl . '/pagos';

        $ch = curl_init($url);

        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 10,
        ]);

        $response = curl_exec($ch);

        if ($response === false) {
            throw new RuntimeException('Error al conectar con Odoo');
        }

        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new RuntimeException('Respuesta inválida de Odoo');
        }

        $decoded = json_decode($response, true);

        if (!is_array($decoded)) {
            throw new RuntimeException('JSON inválido desde Odoo');
        }

        return $decoded;
    }
}