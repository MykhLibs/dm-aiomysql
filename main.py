import asyncio
from dm_aiomodbus import DMAioModbusSerialClient, DMAioModbusTcpClient

modbus_client = DMAioModbusSerialClient(port="COM6", name_tag="Ei82kH495", stopbits=1)


async def main():
    res = await modbus_client.read_holding_registers(256, 20)
    print("end", res)

if __name__ == "__main__":
    asyncio.run(main())
