from typing import TYPE_CHECKING, Any, Literal, Protocol, TypeVar, cast

import msgspec
from msgspec import Struct
from msgspec.structs import asdict

__all__ = ["Serializer", "SerializationFormat", "Encoder", "Decoder", "encoder", "decoder", "json_schema", "as_dict"]


type SerializationFormat = Literal["json", "msgpack", "yaml"]

T = TypeVar("T", bound=Struct)


class Encoder(Protocol):
    def __call__(self, data: Struct) -> bytes: ...


class Decoder(Protocol):
    def __call__(self, data: bytes, data_type: type[T]) -> T: ...


def encoder(format: SerializationFormat = "json") -> Encoder:
    """Build specified encoder."""
    encode = None
    match format:
        case "json":
            encode = msgspec.json.encode
        case "msgpack":
            encode = msgspec.msgpack.encode
        case "yaml":
            encode = msgspec.yaml.encode
        case _:
            raise RuntimeError(f"format '{format}'is not supported")
    if TYPE_CHECKING:
        return cast(Encoder, encode)
    return encode


def decoder(format: SerializationFormat = "json") -> Decoder:
    """Build specified decoder."""
    decode = None
    match format:
        case "json":
            decode = msgspec.json.decode
        case "msgpack":
            decode = msgspec.msgpack.decode
        case "yaml":
            decode = msgspec.yaml.decode
        case _:
            raise RuntimeError(f"format '{format}'is not supported")

    if TYPE_CHECKING:
        return cast(Decoder, decode)
    return decode


def json_schema(schema: type[Struct]) -> dict | None:
    """Build json schema for specified schema."""
    if not issubclass(schema, Struct):
        raise RuntimeError(f"schema '{schema}' is not a Struct")
    return msgspec.json.schema(schema)


def as_dict(data: Struct) -> dict[str, Any]:
    """Convert data to dict."""
    return asdict(data)


class Serializer:
    __slots__ = ("_encoder", "_decoder")

    def __init__(self, format: SerializationFormat = "json") -> None:
        super().__init__()
        self._encoder = encoder(format=format)
        self._decoder = decoder(format=format)

    def encode(self, data: Struct) -> bytes:
        return self._encoder(data)

    def decode(self, data: bytes, data_type: type[T]) -> T:
        return self._decoder(data, data_type=data_type)

    def as_dict(self, data: Struct) -> dict[str, Any]:
        return asdict(data)

    def schema(self, schema: type[Struct]) -> dict | None:
        return json_schema(schema=schema)
