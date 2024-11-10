import litestar as ls

from controllers.authentication import AuthenticationController, jwt_auth
from controllers.group_controller import GroupController
from controllers.person_controller import PersonController
from controllers.transaction_controller import TransactionController

app = ls.Litestar(
    route_handlers=[
        AuthenticationController,
        PersonController,
        GroupController,
        TransactionController,
    ],
    on_app_init=[jwt_auth.on_app_init],
)
