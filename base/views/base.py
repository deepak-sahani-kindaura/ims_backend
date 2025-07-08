"""
Base view class for CRUD operations.
This class combines the functionality of CreateView, ListView,
RetrieveView, UpdateView, and DeleteView to provide a standard implementation
"""

from base.views.list import ListView
from base.views.create import CreateView
from base.views.update import UpdateView
from base.views.delete import DeleteView
from base.views.retrieve import RetrieveView


class BaseView(CreateView, ListView, RetrieveView, UpdateView, DeleteView):
    """
    A base view class that combines the functionality of CreateView, ListView,
    RetrieveView, UpdateView, and DeleteView. This class provides a standard
    implementation for handling CRUD operations on objects using the Manager class.
    """

    @classmethod
    def get_method_view_mapping(cls, with_path_id=False):
        if with_path_id:
            return {
                **UpdateView.get_method_view_mapping(),
                **DeleteView.get_method_view_mapping(),
                **RetrieveView.get_method_view_mapping(),
            }

        return {
            **ListView.get_method_view_mapping(),
            **CreateView.get_method_view_mapping(),
        }
