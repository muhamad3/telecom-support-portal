from fastapi import APIRouter, HTTPException, Query

from ..models.schemas import DatasetRecord, DatasetResponse
from ..services import data_service

router = APIRouter(prefix="/api/dataset", tags=["Dataset"])


@router.get(
    "/records",
    response_model=DatasetResponse,
    summary="List dataset records",
    description="Returns paginated customer support records from the sample dataset. "
    "Supports filtering by issue type and free-text search.",
)
async def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    issue_type: str | None = Query(None, description="Filter by issue type"),
    search: str | None = Query(None, description="Search in message and customer fields"),
):
    records, total = data_service.get_records(page, page_size, issue_type, search)
    return DatasetResponse(
        records=records,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/records/{record_id}",
    response_model=DatasetRecord,
    summary="Get a single dataset record",
    description="Returns a single customer support record by its ID.",
)
async def get_record(record_id: int):
    record = data_service.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record
