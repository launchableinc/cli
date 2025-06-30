"""
Test Runner Registry System

This module provides a registry system for collecting test runner functions
before registering them as Typer commands, enabling the NestedCommand where
test runners come before options in command structure.
"""

import inspect
from functools import wraps
from typing import Callable, Dict, List

import typer


class TestRunnerRegistry:
    """Registry for collecting test runner functions by command type."""

    def __init__(self):
        # Dictionary to store test runner functions by command type
        # Format: {command_type: {test_runner_name: function}}
        self._subset_functions: Dict[str, Callable] = {}
        self._record_test_functions: Dict[str, Callable] = {}
        self._split_subset_functions: Dict[str, Callable] = {}

    def register_subset(self, test_runner_name: str, func: Callable):
        """Register a subset function for a test runner."""
        self._subset_functions[test_runner_name] = func

    def register_record_tests(self, test_runner_name: str, func: Callable):
        """Register a record tests function for a test runner."""
        self._record_test_functions[test_runner_name] = func

    def register_split_subset(self, test_runner_name: str, func: Callable):
        """Register a split subset function for a test runner."""
        self._split_subset_functions[test_runner_name] = func

    def get_subset_functions(self) -> Dict[str, Callable]:
        """Get all registered subset functions."""
        return self._subset_functions.copy()

    def get_record_test_functions(self) -> Dict[str, Callable]:
        """Get all registered record test functions."""
        return self._record_test_functions.copy()

    def get_split_subset_functions(self) -> Dict[str, Callable]:
        """Get all registered split subset functions."""
        return self._split_subset_functions.copy()

    def get_all_test_runner_names(self) -> List[str]:
        """Get all unique test runner names across all command types."""
        all_names = set()
        all_names.update(self._subset_functions.keys())
        all_names.update(self._record_test_functions.keys())
        all_names.update(self._split_subset_functions.keys())
        return sorted(list(all_names))


# Global registry instance
_registry = TestRunnerRegistry()


def get_registry() -> TestRunnerRegistry:
    """Get the global test runner registry instance."""
    return _registry


def cmdname(module_name: str) -> str:
    """Figure out the sub-command name from a test runner module name."""
    # a.b.cde -> cde
    # xyz -> xyz
    # In python module name the conventional separator is '_' but in command name,
    # it is '-', so we do replace that
    return module_name[module_name.rfind('.') + 1:].replace('_', '-')


def create_test_runner_wrapper(func: Callable, test_runner_name: str) -> Callable:
    """
    Create a wrapper for test runner functions that handles client injection.

    This preserves the original function signature while adding ctx parameter
    and handling client object injection.
    """
    # Get the original function signature (excluding 'client' parameter)
    sig = inspect.signature(func)
    params = list(sig.parameters.values())[1:]  # Skip 'client' parameter

    # Create a wrapper that matches the original signature
    @wraps(func)
    def typer_wrapper(ctx: typer.Context, *args, **kwargs):
        client = ctx.obj

        # Store the test runner name in the client object for later use
        if hasattr(client, 'set_test_runner'):
            client.set_test_runner(test_runner_name)

        # Call the function with client as first argument, then remaining args
        return func(client, *args, **kwargs)

    # Copy parameter annotations from original function (excluding client)
    new_params = [inspect.Parameter('ctx', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=typer.Context)]
    new_params.extend(params)
    typer_wrapper.__signature__ = sig.replace(parameters=new_params)

    return typer_wrapper
