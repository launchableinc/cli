"""
Dynamic Command Builder for NestedCommand Pattern

This module provides functionality to dynamically generate Typer commands
that combine command-level options with test runner-specific logic,
enabling the NestedCommand pattern where test runners come before options.
"""

import inspect
from typing import Any, Callable, Dict

import typer

from smart_tests.utils.test_runner_registry import get_registry


class DynamicCommandBuilder:
    """Builder for creating dynamic Typer commands using NestedCommand pattern where test runners come before options."""

    def __init__(self):
        self.registry = get_registry()

    def create_subset_commands(self, base_app: typer.Typer,
                               base_callback_func: Callable,
                               base_callback_options: Dict[str, Any]) -> None:
        """
        Create subset commands for each test runner with combined options.

        Args:
            base_app: The Typer app to add commands to
            base_callback_func: The original subset callback function
            base_callback_options: Options from the original subset callback
        """
        subset_functions = self.registry.get_subset_functions()

        for test_runner_name, test_runner_func in subset_functions.items():
            # Create a combined command that merges base options with test runner logic
            combined_command = self._create_combined_subset_command(
                test_runner_name,
                test_runner_func,
                base_callback_func,
                base_callback_options
            )

            # Register the command with the app
            base_app.command(name=test_runner_name, help=f"Subset tests using {test_runner_name}")(combined_command)

    def create_record_test_commands(self, base_app: typer.Typer,
                                    base_callback_func: Callable,
                                    base_callback_options: Dict[str, Any]) -> None:
        """
        Create record test commands for each test runner with combined options.

        Args:
            base_app: The Typer app to add commands to
            base_callback_func: The original record tests callback function
            base_callback_options: Options from the original record tests callback
        """
        record_functions = self.registry.get_record_test_functions()

        for test_runner_name, test_runner_func in record_functions.items():
            # Create a combined command that merges base options with test runner logic
            combined_command = self._create_combined_record_command(
                test_runner_name,
                test_runner_func,
                base_callback_func,
                base_callback_options
            )

            # Register the command with the app
            base_app.command(name=test_runner_name, help=f"Record test results using {test_runner_name}")(combined_command)

    def _create_combined_subset_command(self, test_runner_name: str,
                                        test_runner_func: Callable,
                                        base_callback_func: Callable,
                                        base_callback_options: Dict[str, Any]) -> Callable:
        """Create a combined subset command for a specific test runner."""

        # Get signatures from both functions
        base_sig = inspect.signature(base_callback_func)
        test_runner_sig = inspect.signature(test_runner_func)

        # Combine parameters from both functions
        combined_params = []

        # Add ctx parameter first
        combined_params.append(
            inspect.Parameter('ctx', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=typer.Context)
        )

        # Add parameters from base callback (excluding ctx)
        for param_name, param in base_sig.parameters.items():
            if param_name != 'ctx':
                combined_params.append(param)

        # Add parameters from test runner function (excluding client)
        test_runner_params = list(test_runner_sig.parameters.values())[1:]  # Skip 'client'
        for param in test_runner_params:
            # Avoid duplicate parameter names
            if param.name not in [p.name for p in combined_params]:
                # Ensure parameter has a default value to avoid "non-default follows default" error
                if param.default == inspect.Parameter.empty:
                    # Add a default value for parameters without one
                    param = param.replace(default=None)
                combined_params.append(param)

        # Create the combined function
        def combined_function(*args, **kwargs):
            # Extract ctx from args/kwargs
            ctx = kwargs.get('ctx') or (args[0] if args else None)

            if not ctx:
                raise ValueError("Context not found in function arguments")

            # Store test runner name as context attribute for direct access
            ctx.test_runner = test_runner_name

            # Prepare arguments for base callback
            base_args = {}
            # Unused variable removed

            for i, (param_name, param) in enumerate(base_sig.parameters.items()):
                if param_name == 'ctx':
                    base_args[param_name] = ctx
                elif param_name in kwargs:
                    base_args[param_name] = kwargs[param_name]
                elif i < len(args):
                    base_args[param_name] = args[i]
                elif param.default != inspect.Parameter.empty:
                    base_args[param_name] = param.default

            # Call base callback to set up context
            base_callback_func(**base_args)

            # Get client from context
            client = ctx.obj

            # Store test runner name in client if possible
            if hasattr(client, 'set_test_runner'):
                client.set_test_runner(test_runner_name)

            # Auto-infer base path if not explicitly provided for all test runners
            # This ensures all test runners have access to base_path when needed
            has_base_path_attr = hasattr(client, 'base_path')
            base_path_is_none = client.base_path is None if has_base_path_attr else False
            no_inference_disabled = not kwargs.get('no_base_path_inference', False)

            if has_base_path_attr and base_path_is_none and no_inference_disabled:

                # Attempt to infer base path from current working directory
                try:
                    import pathlib

                    from smart_tests.commands.test_path_writer import TestPathWriter
                    from smart_tests.testpath import FilePathNormalizer

                    file_path_normalizer = FilePathNormalizer()
                    inferred_base_path = file_path_normalizer._auto_infer_base_path(pathlib.Path.cwd().resolve())
                    if inferred_base_path:
                        TestPathWriter.base_path = inferred_base_path
                except (ImportError, OSError) as e:
                    import logging
                    logging.error(f"Failed to infer base path: {e}")
                    # If inference fails, continue with None

            # Prepare arguments for test runner function
            test_runner_args = [client]  # First argument is always client
            test_runner_kwargs = {}

            test_runner_param_names = list(test_runner_sig.parameters.keys())[1:]  # Skip 'client'

            for param_name in test_runner_param_names:
                if param_name in kwargs:
                    test_runner_kwargs[param_name] = kwargs[param_name]

            # Call test runner function
            return test_runner_func(*test_runner_args, **test_runner_kwargs)

        # Set the signature for the combined function
        setattr(combined_function, '__signature__', inspect.Signature(combined_params))
        combined_function.__name__ = f"subset_{test_runner_name.replace('-', '_')}"

        return combined_function

    def _create_combined_record_command(self, test_runner_name: str,
                                        test_runner_func: Callable,
                                        base_callback_func: Callable,
                                        base_callback_options: Dict[str, Any]) -> Callable:
        """Create a combined record test command for a specific test runner."""

        # Get signatures from both functions
        base_sig = inspect.signature(base_callback_func)
        test_runner_sig = inspect.signature(test_runner_func)

        # Combine parameters from both functions
        combined_params = []

        # Add ctx parameter first
        combined_params.append(
            inspect.Parameter('ctx', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=typer.Context)
        )

        # Add parameters from base callback (excluding ctx)
        for param_name, param in base_sig.parameters.items():
            if param_name != 'ctx':
                combined_params.append(param)

        # Add parameters from test runner function (excluding client)
        test_runner_params = list(test_runner_sig.parameters.values())[1:]  # Skip 'client'
        for param in test_runner_params:
            # Avoid duplicate parameter names
            if param.name not in [p.name for p in combined_params]:
                # Ensure parameter has a default value to avoid "non-default follows default" error
                if param.default == inspect.Parameter.empty:
                    # Add a default value for parameters without one
                    param = param.replace(default=None)
                combined_params.append(param)

        # Create the combined function
        def combined_function(*args, **kwargs):
            # Extract ctx from args/kwargs
            ctx = kwargs.get('ctx') or (args[0] if args else None)

            if not ctx:
                raise ValueError("Context not found in function arguments")

            # Store test runner name as context attribute for direct access
            ctx.test_runner = test_runner_name

            # Prepare arguments for base callback
            base_args = {}

            for i, (param_name, param) in enumerate(base_sig.parameters.items()):
                if param_name == 'ctx':
                    base_args[param_name] = ctx
                elif param_name in kwargs:
                    base_args[param_name] = kwargs[param_name]
                elif i < len(args):
                    base_args[param_name] = args[i]
                elif param.default != inspect.Parameter.empty:
                    base_args[param_name] = param.default

            # Call base callback to set up context
            base_callback_func(**base_args)

            # Get client from context
            client = ctx.obj

            # Store test runner name in client if possible
            if hasattr(client, 'set_test_runner'):
                client.set_test_runner(test_runner_name)

            # Prepare arguments for test runner function
            test_runner_args = [client]  # First argument is always client
            test_runner_kwargs = {}

            test_runner_param_names = list(test_runner_sig.parameters.keys())[1:]  # Skip 'client'

            for param_name in test_runner_param_names:
                if param_name in kwargs:
                    test_runner_kwargs[param_name] = kwargs[param_name]

            # Call test runner function
            return test_runner_func(*test_runner_args, **test_runner_kwargs)

        # Set the signature for the combined function
        setattr(combined_function, '__signature__', inspect.Signature(combined_params))
        combined_function.__name__ = f"record_{test_runner_name.replace('-', '_')}"

        return combined_function


def extract_callback_options(callback_func: Callable) -> Dict[str, Any]:
    """
    Extract option definitions from a Typer callback function.

    This function analyzes the signature and annotations of a callback function
    to extract the option definitions that can be reused in dynamic commands.
    """
    sig = inspect.signature(callback_func)
    options = {}

    for param_name, param in sig.parameters.items():
        if param_name == 'ctx':
            continue

        # Store parameter information for later use
        options[param_name] = {
            'annotation': param.annotation,
            'default': param.default,
            'kind': param.kind
        }

    return options
