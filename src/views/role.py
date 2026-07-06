from marshmallow import Schema, fields

class RoleSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

    class Meta:
        fields = ("id", "name")