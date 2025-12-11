from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from engine.models.core import ExchangeApiKeys, User
from playhouse.shortcuts import model_to_dict
from engine.controllers.auth_controller import get_current_user

router = APIRouter()

class StoreExchangeApiKeyRequestJson(BaseModel):
    exchange_name: str
    name: str
    api_key: str
    api_secret: str
    additional_fields: Optional[str] = None

class DeleteExchangeApiKeyRequestJson(BaseModel):
    id: int

class ExchangeSupportedSymbolsRequestJson(BaseModel):
    exchange_name: str

@router.get("/exchange/api-keys")
async def get_api_keys(current_user: User = Depends(get_current_user)):
    keys = []
    for key in ExchangeApiKeys.select():
        k = model_to_dict(key)
        # Mask secret
        k['api_secret'] = '********'
        keys.append(k)
    return keys

@router.post("/exchange/api-keys/store")
async def store_api_key(request: StoreExchangeApiKeyRequestJson, current_user: User = Depends(get_current_user)):
    try:
        ExchangeApiKeys.create(
            exchange_name=request.exchange_name,
            name=request.name,
            api_key=request.api_key,
            api_secret=request.api_secret,
            additional_fields=request.additional_fields
        )
        return {"status": "success", "message": "API key stored"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exchange/api-keys/delete")
async def delete_api_key(request: DeleteExchangeApiKeyRequestJson, current_user: User = Depends(get_current_user)):
    try:
        query = ExchangeApiKeys.delete().where(ExchangeApiKeys.id == request.id)
        rows = query.execute()
        if rows == 0:
             raise HTTPException(status_code=404, detail="API key not found")
        return {"status": "success", "message": "API key deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exchange/supported-symbols")
async def get_supported_symbols(request: ExchangeSupportedSymbolsRequestJson, current_user: User = Depends(get_current_user)):
    # In a real implementation, this would call the exchange adapter
    # For now, we return a mock list based on the exchange name
    if request.exchange_name.lower() == "binance":
        return {"symbols": ["BTC-USDT", "ETH-USDT", "SOL-USDT"]}
    elif request.exchange_name.lower() == "sandbox":
        return {"symbols": ["BTC-USDT", "ETH-USDT"]}
    else:
        return {"symbols": []}
