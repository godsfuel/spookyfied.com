<?php
header('Content-Type: application/json');

$response = [
    "server" => "bounceairbags.com",
    "status" => "active",
    "directory_sync" => "connected",
    "timestamp" => time()
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>