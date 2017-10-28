
import types

from nanohttp import Controller, context, json, RestController, action, etag

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
    @etag(tag=lambda: context.application.version)
    def metadata(self):
        return self.__model__.json_metadata()


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
        context.jsonpatch = True
        db_session = db.get_session()
        try:
            for patch in patches:
                context.form = patch.get('value', {})
                context.method = patch['op']

                remaining_paths = patch['path'].split('/')
                if remaining_paths and not remaining_paths[0]:
                    return_data = self()
                else:
                    return_data = self(*remaining_paths)

                if isinstance(return_data, types.GeneratorType):
                    results.append('"%s"' % ''.join(list(return_data)))
                else:
                    results.append(return_data)

                db_session.flush()
            db_session.commit()
            return '[%s]' % ',\n'.join(results)
        except:
            if db_session.is_active:
                db_session.rollback()
            raise
        finally:
            del context.jsonpatch
