import os
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import DEFAULT_SETTINGS, UPLOAD_DIR
from ..db import db
from ..services.file_service import save_upload_file

import docxf

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = BASE_DIR / "template.docx"


def create_contract_pdf(data: Dict[str, Any]) -> Dict[str, Any]:
    """Генерирует PDF файл договора и возвращает его имя/содержимое."""
    output_dir = UPLOAD_DIR / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

    settings = db.settings.find_one({"type": DEFAULT_SETTINGS["type"]}) or DEFAULT_SETTINGS
    payload = {**settings, **data}

    filler = docxf.DOCXFiller(
        template_path=str(TEMPLATE_PATH),
        output_directory=str(output_dir),
        output_pdf=True,
        keep_docx=False,
        **payload,
    )

    pdf_path = Path(filler.pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF was not created: {pdf_path}")

    with open(pdf_path, "rb") as f:
        content = f.read()

    return {
        "name": pdf_path.name,
        "content": content,
        "path": str(pdf_path),
    }


def attach_contract_pdf_to_owners(user_id: str, car_id: Optional[str], data: Dict[str, Any]) -> None:
    """Создаёт PDF договор и сохраняет его в файловой системе для пользователя и автомобиля."""
    pdf_info = create_contract_pdf(data)
    save_upload_file(user_id, "user", pdf_info["name"], pdf_info["content"])
    if car_id:
        save_upload_file(car_id, "car", pdf_info["name"], pdf_info["content"])
