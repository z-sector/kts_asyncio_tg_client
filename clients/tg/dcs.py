from typing import ClassVar, Type, List

from marshmallow_dataclass import dataclass
from marshmallow import Schema, EXCLUDE


@dataclass
class Message:
    pass


@dataclass
class UpdateObj:
    pass


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: List[UpdateObj]

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class File:
    pass


@dataclass
class GetFileResponse:
    ok: bool
    result: File

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE
