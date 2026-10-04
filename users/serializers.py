from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    A serializer does two jobs:

    1. Model instance -> JSON-ready dict   (serialization / output)
    2. Request body   -> validated Python data (deserialization / input)

    `ModelSerializer` is a shortcut that reads the model and generates the
    fields *and* their validation rules for us, so we do not repeat ourselves.
    """

    class Meta:
        model = User

        # Only expose what the API needs. `created_at` exists on the model and
        # in the database, but we leave it out of the API surface here. Add it
        # to this list if you want it in responses.
        fields = ["id", "name", "email"]

        # `id` is assigned by the database, so clients must never send it.
        read_only_fields = ["id"]

    # Where the validation comes from (no extra code needed):
    # - Required fields: ModelSerializer makes non-null model fields required,
    #   so omitting `name` or `email` fails validation.
    # - Email format: `EmailField` checks that the address looks valid.
    # - Uniqueness: `email` has unique=True on the model, so DRF adds a
    #   UniqueValidator -> duplicate emails return HTTP 400 automatically.
