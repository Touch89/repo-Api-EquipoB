<?php

declare(strict_types=1);

namespace App\Services;

use RuntimeException;

final class PrestashopService
{
    private string $baseUrl;
    private string $apiKey;

    public function __construct()
    {
        $this->baseUrl = 'http://localhost:8080/api';
        $this->apiKey  = 'Admin123';
    }

    public function getPagos(): array
    {
        $url = $this->baseUrl . '/payments';

        $ch = curl_init($url);

        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPAUTH       => CURLAUTH_BASIC,
            CURLOPT_USERPWD        => $this->apiKey . ':',
            CURLOPT_TIMEOUT        => 10,
        ]);

        $response = curl_exec($ch);

        if ($response === false) {
            throw new RuntimeException('Error al conectar con Prestashop');
        }

        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new RuntimeException('Respuesta inválida de Prestashop');
        }

        $decoded = json_decode($response, true);

        if (!is_array($decoded)) {
            throw new RuntimeException('JSON inválido desde Prestashop');
        }

        return $decoded;
    }
}