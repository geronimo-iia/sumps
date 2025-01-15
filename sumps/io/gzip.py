from gzip import compress as _compress
from gzip import decompress as _decompress
from typing import Annotated

from msgspec import Meta, Struct, field

__all__ = ["GzipCompression"]


class GzipCompression(Struct):
    compresslevel: Annotated[int, Meta(gt=0, lt=10, description="gzip compress level")] = field(default=7)

    # _compress: ClassVar[Callable] = _compress
    # decompress : ClassVar[Callable[[bytes], bytes]] = _decompress

    def compress(self, data: bytes) -> bytes:
        return _compress(data=data, compresslevel=self.compresslevel)

    def decompress(self, data: bytes) -> bytes:
        return _decompress(data=data)
