from fastapi import APIRouter, Depends, HTTPException

from ..config_store import ConfigStore
from ..models import Credentials, CredentialsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


def get_store() -> ConfigStore:
    return ConfigStore()


@router.get("", response_model=Credentials)
def get_settings(store: ConfigStore = Depends(get_store)) -> Credentials:
    creds = store.get_credentials()
    return Credentials(username=creds.username, password=creds.password)


@router.put("", response_model=Credentials)
def update_settings(
    body: CredentialsUpdate,
    store: ConfigStore = Depends(get_store),
) -> Credentials:
    return store.update_credentials(body.username, body.password)
