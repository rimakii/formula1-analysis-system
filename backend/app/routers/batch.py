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

@router.post("/import-drivers")
async def batch_import_drivers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Батчевая загрузка пилотов из CSV файла.
    Требуется роль администратора.

    CSV должен содержать колонки: driverRef, forename, surname, code, number, nationality, dob
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        loader = BatchLoader(db)
        result = loader.load_drivers(df)

        return {
            "message": "Загрузка завершена",
            "imported": result["success"],
            "failed": result["failed"],
            "errors": result["errors"][:10]  # Первые 10 ошибок
        }
    except Exception as e:
        logger.error(f"Ошибка при загрузке пилотов: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")

@router.post("/import-constructors")
async def batch_import_constructors(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Батчевая загрузка команд из CSV файла.
    Требуется роль администратора.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        loader = BatchLoader(db)
        result = loader.load_constructors(df)

        return {
            "message": "Загрузка завершена",
            "imported": result["success"],
            "failed": result["failed"],
            "errors": result["errors"][:10]
        }
    except Exception as e:
        logger.error(f"Ошибка при загрузке команд: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")

@router.post("/import-results")
async def batch_import_results(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Батчевая загрузка результатов гонок из CSV файла.
    Требуется роль администратора.

    Выполняется в фоне из-за большого объема данных (>25,000 записей).
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        loader = BatchLoader(db)

        # Запускаем загрузку в фоне для больших файлов
        if len(df) > 1000:
            background_tasks.add_task(loader.load_results_async, df)
            return {
                "message": "Загрузка запущена в фоновом режиме",
                "total_records": len(df),
                "status": "processing"
            }
        else:
            result = loader.load_results(df)
            return {
                "message": "Загрузка завершена",
                "imported": result["success"],
                "failed": result["failed"],
                "errors": result["errors"][:10]
            }
    except Exception as e:
        logger.error(f"Ошибка при загрузке результатов: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")

@router.get("/import-status")
async def get_import_status(
    current_user = Depends(require_admin)
):
    """
    Получить статус выполнения батчевых операций.
    """
    return {
        "message": "Статус импорта",
        "note": "Функционал отслеживания статуса в разработке"
    }

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
