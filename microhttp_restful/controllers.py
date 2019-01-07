
import types

from urllib.parse import parse_qs

from nanohttp import (
    Controller,
    context,
    json,
    RestController,
    action,
    HTTPStatus
)

from microhttp.ext import db


class RootController(Controller):

    def __call__(self, *remaining_paths):

        if context.method == 'options':
            context.response_encoding = 'utf-8'
            context.response_headers.add_header("Cache-Control", "no-cache,no-store")
            return b''

        return super().__call__(*remaining_paths)


class ModelRestController(RestController):
    __model__ = None

    @json
    def metadata(self):
        return self.__model__.json_metadata()


def split_path(url):
    if '?' in url:
        path, query = url.split('?')
    else:
        path, query = url, ''

    return path, {k: v[0] if len(v) == 1 else v for k, v in parse_qs(
        query,
        keep_blank_values=True,
        strict_parsing=False
    ).items()}


class JsonPatchControllerMixin:

    @action(content_type='application/json')
    def patch(self: Controller):
        """
        Set context.method
        Set context.form
        :return:
        """
        # Preserve patches
        patches = context.form
        results = []
        context.suppress_db_commit = True
        db_session = db.get_session()
        try:
            for patch in patches:
                path, context.query = split_path(patch['path'])
                context.form = context.query
                context.form.update(patch.get('value') or {})
                context.method = patch['op'].lower()

                remaining_paths = path.split('/')
                try:
                    if remaining_paths and not remaining_paths[0]:
                        return_data = self()
                    else:
                        return_data = self(*remaining_paths)

                except HTTPStatus as e:
                    # Return empty for HTTP 2xx success statuses
                    if 200 < int(e.status[:3]) < 300:
                        db_session.commit()
                        return_data = '""'
                    else:
                        raise

                if isinstance(return_data, types.GeneratorType):
                    results.append('"%s"' % ''.join(list(return_data)))
                else:
                    results.append(return_data)

                db_session.flush()
                context.query = {}

            db_session.commit()
            return '[%s]' % ',\n'.join(results)

        except Exception:
            if db_session.is_active:
                db_session.rollback()
            raise

        finally:
            del context.suppress_db_commit
