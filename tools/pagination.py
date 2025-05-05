import rest_framework.pagination


class CursorPagination(rest_framework.pagination.CursorPagination):
    ordering = 'id'
