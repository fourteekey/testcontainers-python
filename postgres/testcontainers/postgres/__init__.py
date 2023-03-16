#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os
from typing import Optional
from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

ADDITIONAL_TRANSIENT_ERRORS = []
try:
    from sqlalchemy.exc import DBAPIError
    ADDITIONAL_TRANSIENT_ERRORS.append(DBAPIError)
except ImportError:
    pass


class PostgresContainer(DbContainer):
    """
    Postgres database container.

    Example:

        The example spins up a Postgres database and connects to it using the :code:`psycopg`
        driver.

        .. doctest::

            >>> from testcontainers.postgres import PostgresContainer
            >>> import sqlalchemy

            >>> postgres_container = PostgresContainer("postgres:9.5")
            >>> with postgres_container as postgres:
            ...     engine = sqlalchemy.create_engine(postgres.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("select version()"))
            ...         version, = result.fetchone()
            >>> version
            'PostgreSQL 9.5...'
    """
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "test")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "test")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "test")
    DEFAULT_DRIVER = "psycopg2"

    def __init__(self, image: str = "postgres:latest", port: int = 5432, user: Optional[str] = None,
                 password: Optional[str] = None, dbname: Optional[str] = None,
                 driver: Optional[str] = None, **kwargs) -> None:
        if driver is None:
            driver = self.DEFAULT_DRIVER

        super(PostgresContainer, self).__init__(image=image, **kwargs)
        self.POSTGRES_USER = user or self.POSTGRES_USER
        self.POSTGRES_PASSWORD = password or self.POSTGRES_PASSWORD
        self.POSTGRES_DB = dbname or self.POSTGRES_DB
        self.port_to_expose = port
        self.driver = driver

        self.with_exposed_ports(self.port_to_expose)

    @wait_container_is_ready(*ADDITIONAL_TRANSIENT_ERRORS)
    def _connect(self) -> None:
        import sqlalchemy
        engine = sqlalchemy.create_engine(self.get_connection_url(driver=self.DEFAULT_DRIVER))
        conn = engine.connect()
        conn.close()

    def _configure(self) -> None:
        self.with_env("POSTGRES_USER", self.POSTGRES_USER)
        self.with_env("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self.with_env("POSTGRES_DB", self.POSTGRES_DB)

    def get_connection_url(self, host: Optional[str] = None, driver: Optional[str] = None) -> str:
        if driver is None:
            driver = self.driver

        return super()._create_connection_url(
            dialect="postgresql+{}".format(driver), username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD, db_name=self.POSTGRES_DB, host=host,
            port=self.port_to_expose,
        )
