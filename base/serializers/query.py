from rest_framework import serializers
from base.constants import DEFAULT_PAGE_SIZE, DEFAULT_PAGE_NUMBER


class QuerySerializer(serializers.Serializer):
    """
    A base serializer for handling query parameters with pagination.
    """

    is_pagination = serializers.BooleanField(default=True)
    page = serializers.IntegerField(default=DEFAULT_PAGE_NUMBER, min_value=1)
    page_size = serializers.IntegerField(default=DEFAULT_PAGE_SIZE, min_value=1)

    def to_internal_value(self, data):
        """
        Override to_internal_value to ensure that page and page_size are set
        to default values if not provided in the input data.
        """

        data = data.copy()

        if "page" not in data:
            data["page"] = DEFAULT_PAGE_NUMBER

        if "page_size" not in data:
            data["page_size"] = DEFAULT_PAGE_SIZE

        if "is_pagination" not in data:
            data["is_pagination"] = True

        return super().to_internal_value(data)
