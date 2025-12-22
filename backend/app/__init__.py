import logging

logging.basicConfig(
    format="[%(name)s] - %(levelname)s - %(message)s",
    level=logging.INFO
)

app_loger = logging.getLogger("APP_LOG")
