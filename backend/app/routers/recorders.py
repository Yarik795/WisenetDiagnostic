from fastapi import APIRouter, Depends, HTTPException

from ..config_store import ConfigStore
from ..models import (
    CheckResult,
    CheckStatus,
    Recorder,
    RecorderCheckResponse,
    RecorderCreate,
    RecorderUpdate,
)
from ..sunapi import check_recorder

router = APIRouter(prefix="/recorders", tags=["recorders"])


def get_store() -> ConfigStore:
    return ConfigStore()


@router.get("", response_model=list[Recorder])
def list_recorders(store: ConfigStore = Depends(get_store)) -> list[Recorder]:
    return store.list_recorders()


@router.post("", response_model=Recorder, status_code=201)
def create_recorder(
    body: RecorderCreate,
    store: ConfigStore = Depends(get_store),
) -> Recorder:
    return store.create_recorder(body)


@router.put("/{recorder_id}", response_model=Recorder)
def update_recorder(
    recorder_id: str,
    body: RecorderUpdate,
    store: ConfigStore = Depends(get_store),
) -> Recorder:
    updated = store.update_recorder(recorder_id, body)
    if not updated:
        raise HTTPException(status_code=404, detail="Регистратор не найден")
    return updated


@router.delete("/{recorder_id}", status_code=204)
def delete_recorder(
    recorder_id: str,
    store: ConfigStore = Depends(get_store),
) -> None:
    if not store.delete_recorder(recorder_id):
        raise HTTPException(status_code=404, detail="Регистратор не найден")


@router.post("/{recorder_id}/check", response_model=RecorderCheckResponse)
async def check_recorder_endpoint(
    recorder_id: str,
    store: ConfigStore = Depends(get_store),
) -> RecorderCheckResponse:
    recorder = store.get_recorder(recorder_id)
    if not recorder:
        raise HTTPException(status_code=404, detail="Регистратор не найден")

    credentials = store.get_credentials()
    outcome = await check_recorder(recorder, credentials)

    updated = store.update_recorder_status(
        recorder_id,
        outcome.status,
        outcome.checked_at,
        outcome.error,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Регистратор не найден")

    check = CheckResult(
        status=outcome.status,
        checked_at=outcome.checked_at,
        error=outcome.error,
        model=outcome.device.model if outcome.device else None,
        firmware_version=outcome.device.firmware_version if outcome.device else None,
        device_type=outcome.device.device_type if outcome.device else None,
    )
    return RecorderCheckResponse(recorder=updated, check=check)
