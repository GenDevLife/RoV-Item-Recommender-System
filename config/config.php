<?php
$host = 'localhost';
$username = 'root';
$password = '';
$database = 'rov';

// PDO
$pdo = new PDO( "mysql:host={$host}; dbname={$database}", $username, $password, [ PDO::ATTR_EMULATE_PREPARES => false ] );
// OOP mysqli
$mysqli = new mysqli($host, $username, $password, $database );
// Procedural mysqli
$mysqli_p = mysqli_connect($host, $username, $password, $database );

if(!$mysqli_p){
    die("Connection failed".mysqli_connect_error());
}
?>
