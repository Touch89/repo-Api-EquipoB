<?php

declare(strict_types=1);

use App\Controllers\ApiController;
use App\Services\DataService;

$controller = new ApiController(new DataService());

$router->get('/', fn() => [
	'status' => 200,
	'body' => [
		'ok' => true,
		'message' => 'API creada',
	],
]);

$router->get('/api/productos', fn() => $controller->getProductos());
$router->get('/api/categorias', fn() => $controller->getCategorias());


