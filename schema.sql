-- AssetFlow MySQL bootstrap. Django migrations create the full schema.
CREATE DATABASE IF NOT EXISTS assetflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'assetflow_user'@'localhost' IDENTIFIED BY 'change_me';
GRANT ALL PRIVILEGES ON assetflow.* TO 'assetflow_user'@'localhost';
FLUSH PRIVILEGES;
