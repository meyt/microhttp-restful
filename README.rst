microhttp-restful
=================

.. image:: https://travis-ci.org/meyt/microhttp-restful.svg?branch=master
    :target: https://travis-ci.org/meyt/microhttp-restful

.. image:: https://coveralls.io/repos/github/meyt/microhttp-restful/badge.svg?branch=master
    :target: https://coveralls.io/github/meyt/microhttp-restful?branch=master


A tool-chain for create RESTful web applications.

Features:

- SQLAlchemy mixins for:
    - Pagination
    - Ordering
    - Filtering
    - SoftDelete
    - Activation
    - Create/Modify datetime
- HTTP form validation.
- Automatically transform the SQLAlchemy models
  and queries into JSON with standard naming(camelCase).
