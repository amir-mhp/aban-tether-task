import re

from marshmallow import Schema, fields, validate

phone_re = re.compile(r"^09\d{9}$")


class UserSchema(Schema):
    phone = fields.Str(required=True, validate=validate.Regexp(phone_re))
    password = fields.Str(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)


class AuthenticateSchema(Schema):
    phone = fields.Str(required=True, validate=validate.Regexp(phone_re))
    password = fields.Str(required=True)


class SubmitTransactionSchema(Schema):
    currency_id = fields.Str(required=True)
    count = fields.Int(required=True)
