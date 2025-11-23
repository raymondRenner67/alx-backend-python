from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    """
    Pagination class for messages with 20 items per page.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
