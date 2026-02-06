"""Handlers del bot."""
from handlers.commands import setup_command_handlers
from handlers.callbacks import setup_callback_handlers
from handlers.messages import setup_message_handlers

__all__ = ['setup_command_handlers', 'setup_callback_handlers', 'setup_message_handlers']
