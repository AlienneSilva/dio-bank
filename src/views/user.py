from src.app import ma
from src.views.role import RoleSchema
from src.models.user import Usuario
from marshmallow import fields

class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_fk = True

class UserIdParameter(ma.Schema):
    usuario_id = fields.Int(required=True, strict=True)


class CreateUserSchema(ma.Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    role_id = fields.Int(required=True, strict=True)

