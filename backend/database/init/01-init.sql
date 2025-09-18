-- Inicialização do banco de dados GLPI Dashboard
-- Este arquivo é executado automaticamente quando o container MySQL é criado

-- Criar database se não existir
CREATE DATABASE IF NOT EXISTS glpi_dashboard_funcional CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE glpi_dashboard_funcional;

-- Criar tabela de configurações (opcional)
CREATE TABLE IF NOT EXISTS app_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Inserir configurações padrão
INSERT IGNORE INTO app_config (config_key, config_value) VALUES
('app_name', 'GLPI Dashboard'),
('app_version', '1.0.0'),
('last_sync', NOW());

-- Criar usuário específico para a aplicação (se não existir)
CREATE USER IF NOT EXISTS 'glpi_user'@'%' IDENTIFIED BY 'glpi_password';
GRANT ALL PRIVILEGES ON glpi_dashboard_funcional.* TO 'glpi_user'@'%';
FLUSH PRIVILEGES;

-- Mostrar informações do banco
SELECT 'Database GLPI Dashboard initialized successfully' as status;
