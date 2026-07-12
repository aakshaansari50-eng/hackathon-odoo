-- AssetFlow database bootstrap for XAMPP / phpMyAdmin
-- Import this file first in phpMyAdmin. Then run Django migrations (see XAMPP_SETUP.md).
-- Charset utf8mb4 supports all standard text safely.

CREATE DATABASE IF NOT EXISTS `assetflow`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'assetflow_user'@'localhost'
  IDENTIFIED BY 'ChangeThisStrongPassword!';

GRANT ALL PRIVILEGES ON `assetflow`.* TO 'assetflow_user'@'localhost';
FLUSH PRIVILEGES;

USE `assetflow`;
