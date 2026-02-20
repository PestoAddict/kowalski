from typing import Optional
import io

from fastapi.responses import StreamingResponse
from fastapi import APIRouter, File, UploadFile

from src.services.city_filter_extender import city_filter_extender

router = APIRouter(tags=["extend_city-filter"])

@router.post("/extend_city_filter/")
async def extend_city_filter(
    new_filename: Optional[str] = "new_city_filter.txt",
    txt_file: UploadFile = File(...)):
    """Эндпоинт позволяет расширить фильтр направлений. \n
    Принимает в себя файл .txt с Вашими направлениями.\n
    И возвращает расширенный список те для каждого перелета он делает перелеты:\n
        - туда\n
        - обратно\n
        - туда-обратно\n
        - обратно-туда\n

    пример содержимого вашего файла:\n
        KHI-MCX\n
        KHI-LED\n
        LED-KHI\n
        LHE-KHI|KHI-LHE\n

    какой файл получите в ответ:\n
        KHI-MCX\n
        MCX-KHI\n
        KHI-MCX|MCX-KHI\n
        MCX-KHI|KHI-MCX\n
        KHI-LED\n
        LED-KHI\n
        KHI-LED|LED-KHI\n
        LED-KHI|KHI-LED\n
        KHI-LHE\n
        LHE-KHI\n
        KHI-LHE|LHE-KHI\n
        LHE-KHI|KHI-LHE\n
                """
    content = await txt_file.read()

    new_filter = city_filter_extender.process_city_filter(file_content=content)
    file_like = io.StringIO()
    new_filter.to_csv(file_like, index=False, header=False)
    file_like.seek(0)
    response = StreamingResponse(file_like, media_type="text/plain")
    response.headers["Content-Disposition"] = f"attachment; filename={new_filename}"
    return response
