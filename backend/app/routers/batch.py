from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io
from app.database import get_db
from app.auth.dependencies import require_admin
from app.services.batch_loader import BatchLoader
import logging

router = APIRouter(prefix="/api/batch", tags=["Batch Operations"])
logger = logging.getLogger(__name__)


@router.post("/import-all-kaggle")
async def import_all_kaggle_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Загрузить все данные из Kaggle dataset.
    Файлы должны находиться в /data/kaggle_dataset/

    Требуется роль администратора.
    """
    loader = BatchLoader(db)

    try:
        # Запускаем полную загрузку в фоне
        background_tasks.add_task(loader.load_all_kaggle_data)

        return {
            "message": "Полная загрузка данных Kaggle запущена в фоновом режиме",
            "status": "processing",
            "note": "Проверьте логи backend для отслеживания прогресса"
        }
    except Exception as e:
        logger.error(f"Ошибка при запуске полной загрузки: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
