from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


class FieldVisibility(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


@dataclass
class Field:
    name: str
    visibility: FieldVisibility
    value: Optional[str] = None


@dataclass
class Contract:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    fields: list[Field] = field(default_factory=list)


@dataclass
class Provider:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    contracts: list[Contract] = field(default_factory=list)


@dataclass
class User:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    providers: list[Provider] = field(default_factory=list)