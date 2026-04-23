from enum import Enum
from typing import Optional
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_index():
    return FileResponse("static/index.html")


class FieldVisibility(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class FieldIn(BaseModel):
    name: str
    visibility: FieldVisibility
    value: Optional[str] = None


class ContractIn(BaseModel):
    name: str
    provider_id: str
    fields: list[FieldIn] = []


class ProviderIn(BaseModel):
    name: str


class FieldOut(BaseModel):
    id: str
    name: str
    visibility: FieldVisibility
    value: Optional[str] = None


class ContractOut(BaseModel):
    id: str
    name: str
    provider_id: str
    provider_name: str
    fields: list[FieldOut]


class ProviderOut(BaseModel):
    id: str
    name: str


class UserIn(BaseModel):
    name: str


class UserOut(BaseModel):
    id: str
    name: str
    providers: list[ProviderOut]


db_contracts: dict[str, dict] = {}
db_providers: dict[str, dict] = {}
db_users: dict[str, dict] = {}


def seed_data():
    provider1_id = str(uuid.uuid4())
    provider2_id = str(uuid.uuid4())

    db_providers[provider1_id] = {"id": provider1_id, "name": "AWS"}
    db_providers[provider2_id] = {"id": provider2_id, "name": "Azure"}

    contract1_id = str(uuid.uuid4())
    contract2_id = str(uuid.uuid4())

    db_contracts[contract1_id] = {
        "id": contract1_id,
        "name": "AWS Enterprise",
        "provider_id": provider1_id,
        "fields": [
            {"id": str(uuid.uuid4()), "name": "api_key", "visibility": "private", "value": "secret-key-123"},
            {"id": str(uuid.uuid4()), "name": "region", "visibility": "public", "value": "us-east-1"},
        ],
    }

    db_contracts[contract2_id] = {
        "id": contract2_id,
        "name": "Azure Standard",
        "provider_id": provider2_id,
        "fields": [
            {"id": str(uuid.uuid4()), "name": "tenant_id", "visibility": "private", "value": "tenant-abc"},
            {"id": str(uuid.uuid4()), "name": "subscription", "visibility": "public", "value": "sub-001"},
        ],
    }


seed_data()


@app.get("/contracts", response_model=list[ContractOut])
def list_contracts():
    result = []
    for contract in db_contracts.values():
        provider = db_providers.get(contract["provider_id"])
        provider_name = provider["name"] if provider else "Unknown"
        result.append(
            ContractOut(
                id=contract["id"],
                name=contract["name"],
                provider_id=contract["provider_id"],
                provider_name=provider_name,
                fields=contract["fields"],
            )
        )
    return result


@app.get("/contracts/{contract_id}", response_model=ContractOut)
def get_contract(contract_id: str):
    contract = db_contracts.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    provider = db_providers.get(contract["provider_id"])
    provider_name = provider["name"] if provider else "Unknown"
    return ContractOut(
        id=contract["id"],
        name=contract["name"],
        provider_id=contract["provider_id"],
        provider_name=provider_name,
        fields=contract["fields"],
    )


@app.post("/contracts", response_model=ContractOut)
def create_contract(contract: ContractIn):
    contract_id = str(uuid.uuid4())
    fields = [{"id": str(uuid.uuid4()), "name": f.name, "visibility": f.visibility, "value": f.value} for f in contract.fields]
    db_contracts[contract_id] = {
        "id": contract_id,
        "name": contract.name,
        "provider_id": contract.provider_id,
        "fields": fields,
    }
    provider = db_providers.get(contract.provider_id)
    provider_name = provider["name"] if provider else "Unknown"
    return ContractOut(
        id=contract_id,
        name=contract.name,
        provider_id=contract.provider_id,
        provider_name=provider_name,
        fields=fields,
    )


@app.get("/providers", response_model=list[ProviderOut])
def list_providers():
    return [ProviderOut(id=p["id"], name=p["name"]) for p in db_providers.values()]