import os
from typing import TypeVar, Callable, Awaitable, Optional, Union
from decimal import Decimal
from mysql.connector.aio import connect as AsyncMysqlConnector
from dm_logger import DMLogger

LB = TypeVar("LB", list, bool)
LD = TypeVar("LD", list, dict)


class DMAioMysqlClient:
    _logger_params = None

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 3306,
        user: str = "",
        password: str = "",
        database: str = "",
    ) -> None:
        self._set_logger()
        self._mysql_config = {
            "host": host,
            "port": int(port),
            "user": user,
            "password": password,
            "database": database
        }

    async def query(
        self,
        query: str,
        params: Union[list, tuple] = None,
        *,
        dict_results: bool = True,
        commit: bool = False
    ) -> LB:
        error_return = False if commit else []

        async def callback(connection: AsyncMysqlConnector) -> LB:
            try:
                cursor = await connection.cursor(dictionary=dict_results)
                await cursor.execute(query, params)
                if commit:
                    await connection.commit()
                    return True
                results = await cursor.fetchall()
                results = self._convert_decimal_to_float(results)
                return results
            except Exception as e:
                self._logger.error(f"Query error: {e}")
            return error_return

        return await self._execute(callback, error_return)

    async def insert_one(
        self,
        table_name: str,
        data: dict
    ) -> bool:
        return await self.insert_many(table_name, data=[data])

    async def insert_many(
        self,
        table_name: str,
        data: list[dict]
    ) -> bool:
        keys = data[0].keys()
        columns = ", ".join(k for k in keys)
        values_mask = ", ".join("%s" for _ in range(len(keys)))
        query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({values_mask})"
        values = [list(item.values()) for item in data]

        async def callback(connection: AsyncMysqlConnector) -> bool:
            try:
                cursor = await connection.cursor(dictionary=True)
                await cursor.executemany(query, values)
                await connection.commit()
                return True
            except Exception as e:
                self._logger.error(f"Query error: {e}")
            return False

        return await self._execute(callback)

    async def _execute(
        self,
        callback: Callable[[AsyncMysqlConnector], Awaitable[LB]],
        error_return: LB = False
    ) -> Optional[LB]:
        try:
            async with await AsyncMysqlConnector(**self._mysql_config) as connection:
                return await callback(connection)
        except Exception as e:
            self._logger.error(f"Callback error: {e}")
        return error_return

    @staticmethod
    def _convert_decimal_to_float(results: LD) -> LD:
        new_results = []
        for row in results:
            if isinstance(row, dict):
                for k, v in row.items():
                    if isinstance(v, Decimal):
                        row[k] = float(v)
                new_results.append(row)
            else:
                new_row = []
                for v in row:
                    if isinstance(v, Decimal):
                        v = float(v)
                    new_row.append(v)
                new_results.append(new_row)
        return new_results

    def _set_logger(self) -> None:
        params = {"name": self.__class__.__name__}
        if isinstance(self._logger_params, dict):
            params.update(self._logger_params)
        self._logger = DMLogger(**params)

    @classmethod
    def set_logger_params(cls, extra_params = None) -> None:
        if isinstance(extra_params, dict) or extra_params is None:
            cls._logger_params = extra_params


class DMAioEnvMysqlClient(DMAioMysqlClient):
    _logger_params = None

    def __init__(self, env_prefix: str = "MYSQL"):
        env_prefix = env_prefix or "MYSQL"
        host = os.getenv(f"{env_prefix}_HOST", "127.0.0.1")
        port = os.getenv(f"{env_prefix}_PORT", 3306)
        username = os.getenv(f"{env_prefix}_USERNAME", "")
        password = os.getenv(f"{env_prefix}_PASSWORD", "")
        database = os.getenv(f"{env_prefix}_DATABASE", "")

        if not (host and port and username and password and database):
            self._set_logger()
            self._logger.critical(f"{env_prefix} env variables not set! Set env variables: "
                                  f"{env_prefix}_HOST, {env_prefix}_PORT, {env_prefix}_USERNAME, "
                                  f"{env_prefix}_PASSWORD, {env_prefix}_DATABASE")
            exit(-55)

        super().__init__(host, port, username, password, database)
        self._set_logger()
