from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ContactGroupCreate(BaseModel):
    name: str
    notes: str | None = None


class ContactGroupUpdate(BaseModel):
    name: str | None = None
    notes: str | None = None


class PhoneNumberOut(BaseModel):
    id: int
    number: str
    label: str | None
    group_id: int | None
    sequence_num: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactGroupOut(BaseModel):
    id: int
    name: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    phone_numbers: list[PhoneNumberOut] = []

    model_config = {"from_attributes": True}


class PhoneNumberCreate(BaseModel):
    number: str
    label: str | None = None
    group_id: int | None = None


class PhoneNumberAssign(BaseModel):
    group_id: int


class DialRequest(BaseModel):
    number: str
    contact_id: int | None = None


class MergeRequest(BaseModel):
    line_ids: list[str]


class LineOut(BaseModel):
    line_id: str
    status: str
    number: str
    contact_name: str | None = None
    started_at: float | None = None
    merged_with: list[str] = []


class TTSGenerateRequest(BaseModel):
    text: str
    voice_id: str


class VoiceOut(BaseModel):
    voice_id: str
    name: str
    preview_url: str | None = None


class ClipOut(BaseModel):
    id: str
    label: str
    voice_id: str
    voice_name: str | None
    file_path: str
    pinned: bool
    duration: float | None = None
    created_at: datetime | None = None
    source: str = "generated"

    model_config = {"from_attributes": True}


class LegacyClipOut(BaseModel):
    id: int
    persona: str
    label: str
    file_path: str
    category: str | None
    display_order: int | None

    model_config = {"from_attributes": True}


class ModuleCreate(BaseModel):
    name: str
    description: str | None = None


class ModuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ModuleClipOut(BaseModel):
    id: int
    kind: str
    label: str
    file_path: str
    tier: int | None
    expected_duration: float | None
    position: int

    model_config = {"from_attributes": True}


class ModuleClipUpdate(BaseModel):
    label: str | None = None
    tier: int | None = None
    expected_duration: float | None = None


class ModuleSummaryOut(BaseModel):
    id: int
    name: str
    description: str | None
    script_count: int
    filler_count: int
    updated_at: datetime


class ModuleOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    clips: list[ModuleClipOut] = []

    model_config = {"from_attributes": True}


class ModuleReorderRequest(BaseModel):
    kind: Literal["script", "filler"]
    clip_ids: list[int]


class TemplateOut(BaseModel):
    key: str
    name: str
    description: str
    script_count: int
    filler_count: int


class ModuleGenerateRequest(BaseModel):
    name: str
    voice_id: str
    template_key: str | None = None
    source_module_id: int | None = None


class ModuleGenerateOut(BaseModel):
    module: ModuleOut
    total_lines: int


class RouteToggle(BaseModel):
    source: str
    line_id: str
    enabled: bool


class RoutingMatrixOut(BaseModel):
    routes: dict[str, dict[str, bool]]
    mic_muted: bool
