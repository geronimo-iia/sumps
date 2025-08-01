"""Unit tests configuration file."""

import logging

import curio
import pytest

parametrize = pytest.mark.parametrize


def pytest_configure(config):
    """Disable verbose output when running tests."""
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)

    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False

    config.addinivalue_line("markers",
                            "curio: "
                            "mark the test as a coroutine, it will be "
                            "run using a curio kernel")
    
# we didnt use pytest-curio as we will made test on sumps.Kernel
@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(collector, name, obj):
    """A pytest hook to collect curio coroutines."""
    if collector.funcnamefilter(name) and curio.meta.iscoroutinefunction(obj):
        item = pytest.Function.from_parent(collector, name=name)
        if "curio" in item.keywords:
            return list(collector._genfunctions(name, obj))

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """
    Run curio marked test functions in a kernel instead of a normal
    function call.
    """
    if 'curio' in pyfuncitem.keywords:
        funcargs = pyfuncitem.funcargs
        testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
        with curio.Kernel() as kernel:
            try:
                kernel.run(pyfuncitem.obj(**testargs))
            except curio.TaskError as task_error:
                # raise the cause
                raise task_error.__cause__ from task_error
        return True

