from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from . import services
from .models import User
from .serializers import UserSerializer


@api_view(["GET", "POST"])
def user_list(request: Request) -> Response:
    """
    Collection endpoint: /api/users/

    `@api_view` turns a plain function into a DRF view. It:
      - only allows the HTTP methods listed above (anything else -> HTTP 405),
      - hands us DRF's `Request`, which has `.data` and `.query_params`,
      - lets us return a DRF `Response`, which is rendered as JSON.
    """
    if request.method == "GET":
        # Query parameters: the DRF equivalent of Express's `req.query`.
        #   GET /api/users/?name=John    -> request.query_params["name"]
        #   GET /api/users/?email=a@b.c  -> request.query_params["email"]
        # `.get()` returns None when the parameter is absent.
        name = request.query_params.get("name")
        email = request.query_params.get("email")

        users = services.list_users(name=name, email=email)

        # `many=True` serializes a list of model instances into a list of dicts.
        serializer = UserSerializer(users, many=True)

        # Response() is DRF's version of Express's `res.json()`.
        return Response({"users": serializer.data})

    # --- POST /api/users/ : create a user -----------------------------------
    # `request.data` is the parsed request body (JSON or form data).
    # It is the DRF equivalent of Express's `req.body`.
    data = request.data

    # Hand the raw input to the serializer to be validated and converted.
    serializer = UserSerializer(data=data)

    # `is_valid()` runs every validation rule (required, format, uniqueness...).
    # We call it explicitly (instead of raise_exception=True) so beginners can
    # see exactly what a failed validation looks like.
    if not serializer.is_valid():
        # `serializer.errors` is a dict like
        #   {"email": ["Enter a valid email address."]}
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Validated data is clean, typed Python ready for the ORM.
    user = services.create_user(serializer.validated_data)

    # 201 Created, with a JSON representation of the new user as the body.
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def user_detail(request: Request, id: int) -> Response:
    """
    Single-item endpoint: /api/users/<id>/

    How `id` arrives: `users/urls.py` declares the path `<int:id>/`, so Django
    captures that URL segment and passes it to this function as the argument
    named `id`. In other words:

        GET /api/users/42/   ->   user_detail(request, id=42)

    (The name `id` here matches the `<int:id>` in the URL. Rename one and you
    must rename the other.)
    """
    try:
        user = services.get_user(id)
    except User.DoesNotExist:
        # A missing row is a client error, not a server crash: return 404.
        return Response(
            {"detail": f"User with id={id} does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(UserSerializer(user).data)

    # Want to require login for these endpoints? Add DRF permissions, e.g.:
    #   from rest_framework.decorators import permission_classes
    #   from rest_framework.permissions import IsAuthenticated
    #   @permission_classes([IsAuthenticated])
    # See the "Authentication & permissions" section of the README.
