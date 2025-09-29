#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated, List

UUID_PATTERN = (
    r"^[\da-fA-F]{8}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{12}$"
)


IMSIStr = Annotated[str, StringConstraints(pattern=r'^[1-9]\d{13,15}$')]
MSISDNStr = Annotated[str, StringConstraints(pattern=r'^[1-9]\d{8,13}$')]
UUIDStr = Annotated[str, StringConstraints(pattern=UUID_PATTERN)]
ErrorString = Annotated[str, StringConstraints(max_length=128)]
CountString = Annotated[str, StringConstraints(max_length=3)]

# JSON Schema-like field description used by various payload models


class FieldSchema(BaseModel):
    # Default to string unless specified otherwise
    type: str = Field(default="string", description="JSON schema primitive type")
    # Use aliases to serialize as x-displayName/x-order in OpenAPI while allowing Pythonic names
    x_displayName: str = Field(alias="x-displayName", description="Human-friendly label")
    x_order: int = Field(default=1, alias="x-order", description="Ordering hint for UI")

    # Pydantic v2 config
    model_config = ConfigDict(populate_by_name=True)


# Exceptions
GENERAL_ERROR = "could not {action} - contact support for assistance"


class GeneralError(BaseModel):
    error: ErrorString = Field(
        description="Unexpected error",
        examples=["Unexpected error"],
    )
    id: UUIDStr = Field(
        description="Error ID to use when communicating with customer support",
    )


class ForbiddenError(BaseModel):
    error: ErrorString = Field(
        description="Access forbidden",
        examples=["Access Forbidden"],
    )


class ParseError(BaseModel):
    path: ErrorString = Field(
        description="Path to the invalid field",
        examples=["body -> foo"],
    )
    message: ErrorString = Field(
        description="Description of the problem",
        examples=["string too long"],
    )


class ParseErrors(BaseModel):
    error: ErrorString = Field(
        description="General error message",
        examples=["errors in body"],
    )
    count: CountString = Field(
        description="Number of errors found",
        examples=["2"],
    )
    messages: List[ParseError] = Field(
        description="List of detailed parse errors",
    )


class GenericError(BaseModel):
    returncode: int = Field(
        description="Detailed return code")
    errors: list[str] = Field(
        description="List of the encountered errors when serving the request.")


class NotFoundError(BaseModel):
    returncode: int = Field(
        description="Detailed return code")
    errors: list[str] = Field(
        description="List of the encountered errors when serving the request.")
