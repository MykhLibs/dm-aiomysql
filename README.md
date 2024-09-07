# DM-aiomysql

## Urls

* [PyPI](https://pypi.org/project/dm-aiomysql)
* [GitHub](https://github.com/MykhLibs/dm-aiomysql)

### * Package contains both `asynchronous` and `synchronous` clients

## Usage

### Run in Windows

_If you run async code in **Windows**, set correct selector_

```python
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

### Example of using DMAioMysqlClient

Analogue to `DMAioMysqlClient` is the synchronous client `DMMysqlClient`.

```python
from dm_aiomysql import DMAioMysqlClient
import asyncio


async def main():
    # create client
    mysql_client = DMAioMysqlClient("localhost", 3306, "username", "password", "database")

    # execute query - results is list[list[Any]]
    list_results = await mysql_client.query("SELECT * FROM users")

    # execute query - results is list[dict[str, Any]
    dict_results = await mysql_client.query("SELECT * FROM users", dict_results=True)

    # execute query with params placeholders
    results = await mysql_client.query("SELECT * FROM users WHEN name = %s", params=["John"])

    # commit data
    await mysql_client.query("UPDATE users SET age = %s WHERE id = %s", params=[25, 2], commit=True)

    # insert data
    data = {"id": 1, "name": "John_1", "age": 21}
    await mysql_client.insert_one("my_table", data)

    # insert many data
    data_list = [{"id": 2, "name": "John_2", "age": 22}, {"id": 3, "name": "John_3", "age": 23}]
    await mysql_client.insert_many("users", data_list)


if __name__ == "__main__":
    asyncio.run(main())
```

### Example of using DMAioEnvMysqlClient

`DMAioEnvMysqlClient` fully inherits the `DMAioMysqlClient` class.
But the connection parameters are loaded from the **ENV** variables.

**_The client will not be created until all ENV variables are set._**

Analogue to `DMAioEnvMysqlClient` is the synchronous client `DMEnvMysqlClient`.

```python
from dm_aiomysql import DMAioEnvMysqlClient
from dotenv import load_dotenv, find_dotenv

# load ENV variables
load_dotenv(find_dotenv())

# create default client
mysql_client = DMAioEnvMysqlClient()
# needed ENV variables MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE

# create custom client
custom_mysql_client = DMAioEnvMysqlClient(env_prefix="PROD_MYSQL")  # by default: env_prefix="MYSQL"
# needed ENV variables PROD_MYSQL_HOST, PROD_MYSQL_PORT, ...
```

### Set custom logger

_If you want set up custom logger_

```python
from dm_aiomysql import DMAioMysqlClient


# create custom logger
class MyLogger:
    def debug(self, message):
        pass

    def info(self, message):
        pass

    def warning(self, message):
        print(message)

    def error(self, message):
        print(message)


# set up custom logger for all clients
DMAioMysqlClient.set_logger(MyLogger())
```
