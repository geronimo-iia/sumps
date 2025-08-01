from __future__ import annotations

from .protocol import (
    AsyncHaltable,
    AsyncPausable,
    AsyncServiceEventListener,
    AsyncStartable,
    Haltable,
    Pausable,
    ServiceAsyncController,
    ServiceController,
    ServiceEventListener,
    ServiceState,
    Startable,
    Statuable,
)

__all__ = ["get_controller"]


def get_controller(model) -> ServiceController | ServiceAsyncController:
    if isinstance(model, Startable):
        return DefaultServiceController(wrapped=model)

    if isinstance(model, AsyncStartable):
        return DefaultServiceAsyncController(wrapped=model)

    raise RuntimeError("Service must implement Startable or AsyncStartable protocol")


class StateServiceController(Statuable):
    _state: ServiceState = ServiceState.stopped

    def __init__(self):
        super().__init__()
        self._state = ServiceState.stopped

    @property
    def status(self) -> ServiceState:
        return self._state

    def _check(self, *state: ServiceState) -> bool:
        return self._state in state


class DefaultServiceController(StateServiceController, ServiceController):
    _wrapped: Startable
    _listener: ServiceEventListener | None = None

    def __init__(self, wrapped: Startable, listener: ServiceEventListener | None = None):
        super().__init__()
        self._wrapped = wrapped
        self._listener = listener

    def add_listener(self, listener: ServiceEventListener | None = None) -> ServiceEventListener | None:
        old = self._listener
        self._listener = listener
        return old

    def _notify(self, state: ServiceState):
        previous = self._state
        self._state = state
        if self._listener:
            self._listener(previous=previous, next=self._state)

    def start(self):
        if self._check(ServiceState.stopped):
            self._notify(ServiceState.start_pending)
            self._wrapped.start()
            self._notify(ServiceState.running)

    def stop(self):
        if self._check(ServiceState.running, ServiceState.paused):
            self._notify(ServiceState.stop_pending)
            self._wrapped.stop()
            self._notify(ServiceState.stopped)

    def pause(self):
        if isinstance(self._wrapped, Pausable) and self._check(ServiceState.running):
            self._notify(ServiceState.pause_pending)
            self._wrapped.pause()
            self._notify(ServiceState.paused)

    def resume(self):
        if isinstance(self._wrapped, Pausable) and self._check(ServiceState.paused):
            self._notify(ServiceState.resume_pending)
            self._wrapped.resume()
            self._notify(ServiceState.running)

    def halt(self):
        if isinstance(self._wrapped, Haltable):
            self._notify(ServiceState.halt_pending)
            self._wrapped.halt()
            self._notify(ServiceState.stopped)


class DefaultServiceAsyncController(StateServiceController, ServiceAsyncController):
    _wrapped: AsyncStartable
    _listener: AsyncServiceEventListener | None = None

    def __init__(self, wrapped: AsyncStartable, listener: AsyncServiceEventListener | None = None):
        super().__init__()
        self._wrapped = wrapped
        self._listener = listener

    def add_listener(self, listener: AsyncServiceEventListener | None = None) -> AsyncServiceEventListener | None:
        old = self._listener
        self._listener = listener
        return old

    async def _notify(self, state: ServiceState):
        previous = self._state
        self._state = state
        if self._listener:
            await self._listener(previous=previous, next=self._state)

    async def start(self):
        if self._check(ServiceState.stopped):
            await self._notify(ServiceState.start_pending)
            await self._wrapped.start()
            await self._notify(ServiceState.running)

    async def stop(self):
        if self._check(ServiceState.running, ServiceState.paused):
            await self._notify(ServiceState.stop_pending)
            await self._wrapped.stop()
            await self._notify(ServiceState.stopped)

    async def pause(self):
        if isinstance(self._wrapped, AsyncPausable) and self._check(ServiceState.running):
            await self._notify(ServiceState.pause_pending)
            await self._wrapped.pause()
            await self._notify(ServiceState.paused)

    async def resume(self):
        if isinstance(self._wrapped, AsyncPausable) and self._check(ServiceState.paused):
            await self._notify(ServiceState.resume_pending)
            await self._wrapped.resume()
            await self._notify(ServiceState.running)

    async def halt(self):
        if isinstance(self._wrapped, AsyncHaltable):
            await self._notify(ServiceState.halt_pending)
            await self._wrapped.halt()
            await self._notify(ServiceState.stopped)
