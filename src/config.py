"""
Módulo Centralizado de Configurações e Validação de Segredos (Settings)
=======================================================================
Garante o Padrão de Governança de Variáveis de Ambiente (Env Vars & Secrets) do HC-UFPE.
Carrega o arquivo .env e valida se os parâmetros essenciais e chaves de segurança estão corretos.
"""

import os
import re
import logging
from typing import List
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("config")


def normalizar_mysql_url(raw_url: str, async_driver: bool = True) -> str:
    """Normaliza URLs do MySQL tratando senhas com caracteres especiais (ex: '#')
    e atribuindo o driver correto ('asyncmy' para async ou 'pymysql' para síncrono).
    """
    if not raw_url:
        return ""
    
    # Extrai componentes: mysql://user:password@host:port/database
    match = re.match(r"mysql(?:\+[a-zA-Z0-9_-]+)?://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(.+)", raw_url)
    if match:
        user, pwd, host, port, db = match.groups()
        port_str = f":{port}" if port else ""
        driver = "mysql+asyncmy" if async_driver else "mysql+pymysql"
        return f"{driver}://{user}:{quote_plus(pwd)}@{host}{port_str}/{db}"
    
    # Fallback se não bater o regex padrão
    driver_prefix = "mysql+asyncmy://" if async_driver else "mysql+pymysql://"
    if raw_url.startswith("mysql://"):
        return raw_url.replace("mysql://", driver_prefix, 1)
    return raw_url


class Settings:
    # 1. Configurações do Servidor
    ENV: str = os.getenv("ENV", "development").lower()
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info").lower()
    RAW_ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() for origin in RAW_ALLOWED_ORIGINS.split(",") if origin.strip()
    ]

    # 2. Provedores e Bancos de Dados
    PACIENTE_PROVIDER_TYPE: str = os.getenv("PACIENTE_PROVIDER_TYPE", "POSTGRES").upper()
    APP_DB_URL: str = os.getenv("APP_DB_URL", "sqlite+aiosqlite:///data/app.db")
    POSTGRES_DSN: str = os.getenv("POSTGRES_DSN", "")
    ORACLE_DSN: str = os.getenv("ORACLE_DSN", "")

    # 3. Active Directory (LDAP)
    AD_URL: str = os.getenv("AD_URL", "")
    AD_BASEDN: str = os.getenv("AD_BASEDN", "DC=ebserhnet,DC=gov,DC=br")
    AD_BIND_USER: str = os.getenv("AD_BIND_USER", "")
    AD_BIND_PASSWORD: str = os.getenv("AD_BIND_PASSWORD", "")

    # 4. Segurança e Criptografia (JWT)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    JWT_EXP_HOURS: int = int(os.getenv("JWT_EXP_HOURS", "24"))
    REFRESH_TOKEN_EXP_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXP_DAYS", "30"))

    # 5. Notificações Microsoft Teams (CIHDOTT / Busca Ativa)
    TEAMS_WEBHOOK_URL: str = os.getenv("TEAMS_WEBHOOK_URL", "")
    TEAMS_NOTIFICACOES_ATIVO: bool = os.getenv("TEAMS_NOTIFICACOES_ATIVO", "true").lower() in ("true", "1", "yes")
    NOTIFICACOES_MAX_RETENTATIVAS: int = int(os.getenv("NOTIFICACOES_MAX_RETENTATIVAS", "3"))

    # 6. Banco de Dados MySQL (Sistema CSH - Ingestão de Óbitos)
    CSH_MYSQL_URL: str = os.getenv("CSH_MYSQL_URL", "")
    CSH_POLLING_ATIVO: bool = os.getenv("CSH_POLLING_ATIVO", "true").lower() in ("true", "1", "yes")
    CSH_POLLING_INTERVALO_SEGUNDOS: int = int(os.getenv("CSH_POLLING_INTERVALO_SEGUNDOS", "60"))
    CSH_ID_TIPO_MATERIAL_OBITO: int = int(os.getenv("CSH_ID_TIPO_MATERIAL_OBITO", "12"))
    CSH_ID_LOCAL_TRIAGEM_OBSTETRICA: int = int(os.getenv("CSH_ID_LOCAL_TRIAGEM_OBSTETRICA", "923"))

    @classmethod
    def validate_config(cls):
        """Valida a integridade das configurações e dispara avisos de segurança."""
        if cls.ENV == "production":
            if "change-in-production" in cls.JWT_SECRET or "SUA_CHAVE_SECRETA" in cls.JWT_SECRET:
                logger.error(
                    "❌ ERRO CRÍTICO DE SEGURANÇA: A variável 'JWT_SECRET' está usando a chave padrão. "
                    "Altere para uma chave secreta aleatória forte no arquivo .env antes de rodar em produção!"
                )
            if not cls.AD_URL:
                logger.warning(
                    "⚠️ AVISO: Variável 'AD_URL' não definida em produção. "
                    "O sistema está operando no modo Mock de desenvolvimento."
                )
        logger.info(f"Configurações carregadas com sucesso. Ambiente: '{cls.ENV.upper()}'")


# Instância global de configurações
settings = Settings()
settings.validate_config()

# Atalhos exportados no nível do módulo
TEAMS_WEBHOOK_URL = settings.TEAMS_WEBHOOK_URL
TEAMS_NOTIFICACOES_ATIVO = settings.TEAMS_NOTIFICACOES_ATIVO
NOTIFICACOES_MAX_RETENTATIVAS = settings.NOTIFICACOES_MAX_RETENTATIVAS
CSH_MYSQL_URL = settings.CSH_MYSQL_URL
CSH_POLLING_ATIVO = settings.CSH_POLLING_ATIVO
CSH_POLLING_INTERVALO_SEGUNDOS = settings.CSH_POLLING_INTERVALO_SEGUNDOS
CSH_ID_TIPO_MATERIAL_OBITO = settings.CSH_ID_TIPO_MATERIAL_OBITO
CSH_ID_LOCAL_TRIAGEM_OBSTETRICA = settings.CSH_ID_LOCAL_TRIAGEM_OBSTETRICA
