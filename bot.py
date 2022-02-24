import logging
from datetime import datetime

from aiogram import executor

from database import db
from handlers import regisration_handlers, reg_update_handlers
from loader import dp
date_time = datetime.now()
logging.basicConfig(level=logging.DEBUG,
                    filename="logs.txt",
                    datefmt=f"{date_time.strftime('%b %d %Y %H:%M:%S')}",
                    filemode="w",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    db.sql_start()
    regisration_handlers(dp)
    reg_update_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
