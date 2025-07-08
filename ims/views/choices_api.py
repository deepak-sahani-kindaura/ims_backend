from rest_framework.viewsets import ViewSet
from drf_spectacular.utils import extend_schema

from stock.constants import StockMovementEnum
from auth_user.constants import MethodEnum, RoleEnum
from notification.constants import NotificationTypeEnum
from tenant.constants import (
    AuthenticationTypeEnum,
    DatabaseStrategyEnum,
    DatabaseServerEnum,
)

from utils.constants import SeverityEnum
from utils.response import generate_response


def choice_tuple_to_dict(choices):
    """
    Converts a list of choice tuples into a list of dictionaries with 'value' and 'label' keys.
    Args:
        choices (Iterable[Tuple[Any, Any]]): An iterable of tuples, where each tuple contains two elements:
            - The first element is the value.
            - The second element is the label.
    Returns:
        List[dict]: A list of dictionaries, each with 'value' and 'label' keys corresponding to the tuple elements.
    Example:
        >>> choice_tuple_to_dict([(1, 'One'), (2, 'Two')])
        [{'value': 1, 'label': 'One'}, {'value': 2, 'label': 'Two'}]
    """

    return [{"value": ch[0], "label": ch[1]} for ch in choices]


class ConstantsAPIView(ViewSet):
    """
    Retrieve various constant choices used throughout the application.
    """

    @extend_schema(exclude=True)
    def get_constants(self, request):
        """
        Retrieve various constant choices used throughout the application.
        This method collects and returns several enumerated types (such as roles, methods, severity levels, etc.)
        as dictionaries, making them available for frontend or API consumers. The constants are converted from
        their respective Enum choices to dictionary format for easier consumption.
        Args:
            request: The HTTP request object.
        Returns:
            Response: A response object containing a dictionary of constant types.
        """

        data = {}

        data["role_types"] = choice_tuple_to_dict(RoleEnum.choices)
        data["method_types"] = choice_tuple_to_dict(MethodEnum.choices)
        data["severity_types"] = choice_tuple_to_dict(SeverityEnum.choices)
        data["stock_types"] = choice_tuple_to_dict(StockMovementEnum.choices)
        data["notification_types"] = choice_tuple_to_dict(NotificationTypeEnum.choices)
        data["authentication_types"] = choice_tuple_to_dict(
            AuthenticationTypeEnum.choices
        )
        data["database_strategy_types"] = choice_tuple_to_dict(
            DatabaseStrategyEnum.choices
        )
        data["database_server_types"] = choice_tuple_to_dict(DatabaseServerEnum.choices)

        return generate_response(data=data)
