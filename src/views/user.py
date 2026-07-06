from src.app import ma
from src.views.role import RoleSchema
from marshmallow import fields

class UsuarioSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    role_id = fields.Int()
    # Declarado aqui em cima para o Meta conseguir enxergar!
    role = fields.Nested(RoleSchema) 

    class Meta:
        fields = ("id", "username", "role")


class CreateUserSchema(ma.Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    role_id = fields.Int(required=True)

