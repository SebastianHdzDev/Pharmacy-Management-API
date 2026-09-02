import contextvars

# Esta variable almacenará el ID del usuario actual durante el tiempo de vida del request HTTP
current_user_id = contextvars.ContextVar('current_user_id', default=None)
