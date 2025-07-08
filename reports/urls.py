from django.urls import path

from reports.views import ReportViewSet

urlpatterns = [
    path(
        "report/stock-summary",
        ReportViewSet.as_view({"get": "get_stock_summary"}),
        name="stock-summary",
    ),
]
