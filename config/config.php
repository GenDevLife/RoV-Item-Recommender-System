<?php
// config/config.php

// อ่านไฟล์ .env (รูปแบบ key=value ต่อบรรทัด)
$env = parse_ini_file(__DIR__ . '/.env', false, INI_SCANNER_RAW);

// กำหนด default ถ้าไม่มีค่าใน .env
$host     = $env['DB_HOST']         ?? 'localhost';
$port     = $env['DB_PRIMARY_PORT'] ?? '3306';
$dbname   = $env['DB_NAME']         ?? 'rov';
$user     = $env['DB_USER']         ?? 'root';
$password = $env['DB_PASSWORD']     ?? '';

// สร้าง DSN
$dsn = "mysql:host={$host};port={$port};dbname={$dbname};charset=utf8mb4";

try {
    $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ];
    $pdo = new PDO($dsn, $user, $password, $options);
    return $pdo;
} catch (PDOException $e) {
    die("DB connect failed: " . $e->getMessage());
}
