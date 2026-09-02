from sqlalchemy import event
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.attributes import get_history
from sqlmodel import Session

from backend.context import current_user_id
from backend.models import Auditoria, TokenBloqueado


@event.listens_for(Session, "before_flush")
def registrar_auditoria(session, flush_context, instances):
    usuario_id = current_user_id.get()
    
    # session.new (objects that will be done with INSERT)
    for obj in session.new:
        if not isinstance(obj, Auditoria) and not isinstance(obj, TokenBloqueado):
            crear_registro_auditoria(session, obj, "CREAR", usuario_id)

    # session.dirty (objetos that will be done with UPDATE)
    for obj in session.dirty:
        if not isinstance(obj, Auditoria):
            accion = "ACTUALIZAR"
            # verify if soft delet
            if hasattr(obj, 'estaActivo'):
                historia = get_history(obj, 'estaActivo')
                if historia.deleted and historia.added:
                    if historia.deleted[0] is True and historia.added[0] is False:
                        accion = "ELIMINAR_LOGICO"
                    elif historia.deleted[0] is False and historia.added[0] is True:
                        accion = "RESTAURAR_LOGICO"
            
            crear_registro_auditoria(session, obj, accion, usuario_id)

    # session.deleted (objects that will be done with DELETE)
    for obj in session.deleted:
        if not isinstance(obj, Auditoria):
            crear_registro_auditoria(session, obj, "ELIMINAR", usuario_id)

def crear_registro_auditoria(session, obj, accion, usuario_id):
    try:
        mapper = object_mapper(obj)
        # Get table name
        tabla = mapper.mapped_table.name
        # Get PK value
        pk_values = mapper.primary_key_from_instance(obj)
        pk_str = str(pk_values[0]) if pk_values else "N/A"
        
        auditoria = Auditoria(
            accion=accion,
            tabla_afectada=tabla,
            id_registro=pk_str,
            idUsuario=usuario_id
        )
        session.add(auditoria)
    except Exception:
        # If object is not correctly mapped
        pass
