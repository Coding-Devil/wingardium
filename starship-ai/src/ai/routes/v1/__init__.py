#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from fastapi import APIRouter

import ai.routes.v1.ciq_assistant as ciq_assistant
import ai.routes.v1.cudo_assistant as cudo_assistant
import ai.routes.v1.geninfo_assistant as geninfo_assistant
import ai.routes.v1.infra_assistant as infra_assistant
import ai.routes.v1.wlcluster_assistant as wlcluster_assistant
from ai.routes import API_PREFIX
from ai.routes.v1 import health

__api_version__ = "v1"

PREFIX = f"{API_PREFIX}/{__api_version__}"

_health = APIRouter()
_health.include_router(health.router)
_ciq = APIRouter()
_ciq.include_router(ciq_assistant.router)
_geninfo = APIRouter()
_geninfo.include_router(geninfo_assistant.router)
_infra = APIRouter()
_infra.include_router(infra_assistant.router)
_wlcluster = APIRouter()
_wlcluster.include_router(wlcluster_assistant.router)
_cudo = APIRouter()
_cudo.include_router(cudo_assistant.router)

ROUTE_LIST = [
    _health,
    _ciq,
    _geninfo,
    _infra,
    _wlcluster,
    _cudo,
]

# The tag metadata is not expected to have repeated tags.  If tags are being used across paths,
# then their metadata should be added here, not in the individual route files.
TAG_METADATA = [
    health.tag_metadata,
    ciq_assistant.tag_metadata,
    geninfo_assistant.tag_metadata,
    infra_assistant.tag_metadata,
    wlcluster_assistant.tag_metadata,
    cudo_assistant.tag_metadata,
]

__all__ = [PREFIX, ROUTE_LIST, TAG_METADATA]
