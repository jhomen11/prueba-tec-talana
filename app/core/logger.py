import logging
import sys

# Formato del log: [Hora] [Nivel] [Modulo]: Mensaje
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class LoggerSetup:
    """
    Clase encargada de la configuración global de los logs.
    Se asegura de que todos los logs de la app tengan el mismo formato.
    """
    
    @staticmethod
    def configure_logging():
        # Esto atrapa logs de FastAPI, Uvicorn, SQLAlchemy y tu código.
        logging.basicConfig(
            level=logging.INFO,
            format=LOG_FORMAT,
            datefmt=DATE_FORMAT,
            handlers=[
                logging.StreamHandler(sys.stdout) 
            ]
        )
        
  

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Retorna una instancia de logger para un módulo específico.
        Uso: logger = LoggerSetup.get_logger(__name__)
        """
        return logging.getLogger(name)

# Instancia global o uso estático
logger_config = LoggerSetup()