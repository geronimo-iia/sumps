from curio import CancelledError, TaskGroup, current_task
from transitions import Machine
from transitions.extensions.asyncio import AsyncMachine

__all__ = ["CallingMachine", "AsyncCallingMachine"]


class CallingMachine(Machine):
    def _checked_assignment(self, model, name, func):
        if hasattr(model, name):
            predefined_func = getattr(model, name)

            def nested_func(*args, **kwargs):
                predefined_func()
                func(*args, **kwargs)

            setattr(model, name, nested_func)
        else:
            setattr(model, name, func)


class AsyncCallingMachine(AsyncMachine):
    def _checked_assignment(self, model, name, func):
        if hasattr(model, name):
            predefined_func = getattr(model, name)

            def nested_func(*args, **kwargs):
                predefined_func()
                func(*args, **kwargs)

            setattr(model, name, nested_func)
        else:
            setattr(model, name, func)

    @staticmethod
    async def await_all(partials):  # pyright: ignore[reportIncompatibleMethodOverride]
        async with TaskGroup() as g:
            for func in partials:
                await g.spawn(func)
        return g.results

    async def process_context(self, func, model):
        """
        This function is called by an `AsyncEvent` to make callbacks processed in Event._trigger cancellable.
        Using curio this will result in a try-catch block catching CancelledEvents.
        Args:
            func (partial): The partial of Event._trigger with all parameters already assigned
            model (object): The currently processed model

        Returns:
            bool: returns the success state of the triggered event
        """
        if self.current_context.get() is None:
            self.current_context.set(await current_task())
            if id(model) in self.async_tasks:
                self.async_tasks[id(model)].append(await current_task())
            else:
                self.async_tasks[id(model)] = [await current_task()]
            try:
                res = await self._process_async(func, model)
            except CancelledError:
                res = False
            finally:
                self.async_tasks[id(model)].remove(await current_task())
                if len(self.async_tasks[id(model)]) == 0:
                    del self.async_tasks[id(model)]
        else:
            res = await self._process_async(func, model)
        return res

    async def switch_model_context(self, model):
        for running_task in self.async_tasks.get(id(model), []):
            if self.current_context.get() == running_task or running_task in self.protected_tasks:
                continue
            running_task.cancel()
