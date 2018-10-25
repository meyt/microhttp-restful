from nanohttp import context, HTTPBadRequest


class PaginationMixin:
    __take_header_key__ = 'X_TAKE'
    __skip_header_key__ = 'X_SKIP'
    __max_take__ = 100

    @classmethod
    def paginate_by_request(cls, query=None):
        # noinspection PyUnresolvedReferences
        query = query or cls.query

        try:
            take = int(
                context.query.get('take') or context.environ.get(cls.__take_header_key__) or cls.__max_take__)
        except ValueError:
            take = cls.__max_take__

        try:
            skip = int(context.query.get('skip') or context.environ.get(cls.__skip_header_key__) or 0)
        except ValueError:
            skip = 0

        if take > cls.__max_take__:
            raise HTTPBadRequest()

        context.response_headers.add_header('X-Pagination-Take', str(take))
        context.response_headers.add_header('X-Pagination-Skip', str(skip))
        context.response_headers.add_header('X-Pagination-Count', str(query.count()))
        return query.offset(skip).limit(take)  # [skip:skip + take] Commented by vahid
