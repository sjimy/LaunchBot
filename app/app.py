import datetime
import logging
from app.config import START_TYPE_LUNCH, START_TYPE_DINNER, START_TYPE_ROBOT
from app.models import init_db
from app.server import server_run
from app.utils.file_utils import create_dir
from app.service.meal_service import send_meal_msg


def start(start_type):
    create_dir("logs")
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                        filename=f"logs/{datetime.datetime.now().strftime('%Y-%m')}.log")
    logging.info(f"start type: {start_type}")
    init_db()
    if start_type == START_TYPE_LUNCH or start_type == START_TYPE_DINNER:
        send_meal_msg(start_type)
    elif start_type == START_TYPE_ROBOT:
        server_run()

