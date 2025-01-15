from typing import Any, Literal, TypeVar

import msgspec
from msgspec import Struct
from msgspec.structs import asdict

__all__ = ["Serializer", "SerializationFormat"]

T = TypeVar("T", bound=Struct)

type SerializationFormat = Literal["json", "msgpack", "yaml"]


class Serializer:
    __slots__ = ("_encoder", "_decoder")

    def __init__(self, format: SerializationFormat = "json") -> None:
        super().__init__()
        match format:
            case "json":
                self._encoder = msgspec.json.encode
                self._decoder = msgspec.json.decode
            case "msgpack":
                self._encoder = msgspec.msgpack.encode
                self._decoder = msgspec.msgpack.decode
            case "yaml":
                self._encoder = msgspec.yaml.encode
                self._decoder = msgspec.yaml.decode
            case _:
                raise RuntimeError(f"format '{format}'is not supported")

    def encode(self, data: Struct) -> bytes:
        return self._encoder(data)

    def decode(self, data: bytes, data_type: type[T]) -> T:
        return self._decoder(data, type=data_type)

    def as_dict(self, data: Struct) -> dict[str, Any]:
        return asdict(data)

    def json_schema(self, schema: type[Struct]) -> dict | None:
        return msgspec.json.schema(schema)
