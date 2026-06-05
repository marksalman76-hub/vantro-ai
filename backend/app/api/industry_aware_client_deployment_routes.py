from fastapi import APIRouter
from backend.app.core.industry_aware_client_deployment_resolver import (
    resolve_client_industry_deployment,
    industry_aware_client_deployment_status,
)

router = APIRouter()


@router.get("/client/industry-aware-deployment/status")
def client_industry_aware_deployment_status():
    return industry_aware_client_deployment_status()


@router.post("/client/industry-aware-deployment/resolve")
def client_industry_aware_deployment_resolve(payload: dict):
    return resolve_client_industry_deployment(payload)
