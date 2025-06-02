"""Instrumentation module for Arize and Bedrock monitoring.
This module provides functionality to set up instrumentation for Arize and Bedrock
services. It requires Arize API credentials to be set in environment variables.
"""

from logging import Logger
import os
from arize.otel import register
from openinference.instrumentation.litellm import LiteLLMInstrumentor

ARIZE_SPACE_ID = os.environ["ARIZE_SPACE_ID"]
ARIZE_API_KEY = os.environ["ARIZE_API_KEY"]


def start_instrumentation(logger: Logger) -> None:
    """Initialize and start instrumentation for Arize and Bedrock services.
    This function sets up tracing and monitoring for the application using Arize
    and Bedrock instrumentation. It requires Arize API credentials to be set in
    environment variables.
    Args:
        logger (Logger): A logger instance to record instrumentation status and warnings.
    Returns:
        None: This function does not return anything.
    """
    if not (ARIZE_API_KEY and ARIZE_SPACE_ID):
        logger.warn(
            "ARIZE_API_KEY and ARIZE_SPACE_ID must be set to instrument the application"
        )
        return
    tracer_provider = register(
        space_id=ARIZE_SPACE_ID,
        api_key=ARIZE_API_KEY,
        project_name="recipe-chatbot",  # Will delete the project later on
    )
    LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)
    logger.info("Arize instrumentation started")
