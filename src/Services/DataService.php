<?php

declare(strict_types=1);

namespace App\Services;

use RuntimeException;

final class DataService
{
    private string $dataDir;

    public function __construct(?string $dataDir = null)
    {
        $this->dataDir = $dataDir ?? dirname(__DIR__, 2) . '/data';
    }

    public function getCollection(string $fileName): array
    {
        $fullPath = $this->dataDir . '/' . $fileName;

        if (!file_exists($fullPath)) {
            throw new RuntimeException("Archivo de datos no encontrado: {$fileName}");
        }

        $content = file_get_contents($fullPath);

        if ($content === false) {
            throw new RuntimeException("No se pudo leer el archivo: {$fileName}");
        }

        $decoded = json_decode($content, true);

        if (!is_array($decoded)) {
            throw new RuntimeException("JSON inválido en: {$fileName}");
        }

        return $decoded;
    }
}
