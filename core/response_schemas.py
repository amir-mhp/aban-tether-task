from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Str()
    phone = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    wallet_balance = fields.Float()

    class Meta:
        ordered = True


class AuthenticateSchema(Schema):
    user = fields.Nested(UserSchema())
    token = fields.Str()

    class Meta:
        ordered = True


class CurrencySchema(Schema):
    id = fields.Str()
    title = fields.Str()
    price = fields.Str()
    updated_at = fields.Str()

    class Meta:
        ordered = True


class TransactionSchema(Schema):
    user = fields.Nested(UserSchema())
    amount = fields.Int()
    currency = fields.Nested(CurrencySchema())

    class Meta:
        ordered = True
