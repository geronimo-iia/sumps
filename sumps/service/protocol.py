from enum import Enum
from typing import Protocol, runtime_checkable

__all__ = [
    "ServiceState",
    "Statuable",
    "Startable",
    "Pausable",
    "Haltable",
    "AsyncStartable",
    "AsyncPausable",
    "AsyncHaltable",
    "ServiceEventListener",
    "AsyncServiceEventListener",
    "ServiceController",
    "ServiceAsyncController",
]


class ServiceState(Enum):
    # named state
    stopped = "stopped"
    running = "running"
    paused = "paused"
    # named edge
    start_pending = "start_pending"
    pause_pending = "pause_pending"
    resume_pending = "resume_pending"
    stop_pending = "stop_pending"
    halt_pending = "halt_pending"


@runtime_checkable
class Statuable(Protocol):
    @property
    def status(self) -> ServiceState: ...


@runtime_checkable
class Startable(Protocol):
    def start(self): ...
    def stop(self): ...


@runtime_checkable
class Pausable(Protocol):
    def pause(self): ...
    def resume(self): ...


@runtime_checkable
class Haltable(Protocol):
    def halt(self): ...


@runtime_checkable
class AsyncStartable(Protocol):
    async def start(self): ...
    async def stop(self): ...


@runtime_checkable
class AsyncPausable(Protocol):
    async def pause(self): ...
    async def resume(self): ...


@runtime_checkable
class AsyncHaltable(Protocol):
    async def halt(self): ...


class ServiceEventListener(Protocol):
    def __call__(self, previous: ServiceState, next: ServiceState): ...


class AsyncServiceEventListener(Protocol):
    async def __call__(self, previous: ServiceState, next: ServiceState): ...


class ServiceController(Statuable, Startable, Pausable, Haltable):
    def add_listener(self, listener: ServiceEventListener | None = None) -> ServiceEventListener | None: ...


class ServiceAsyncController(Statuable, AsyncStartable, AsyncPausable, AsyncHaltable):
    def add_listener(self, listener: AsyncServiceEventListener | None = None) -> AsyncServiceEventListener | None: ...
