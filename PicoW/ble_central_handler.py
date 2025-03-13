import asyncio
from bleak import BleakClient

# Known UUIDs and meanings
known_chars = {
    "12345678-1234-5678-1234-567812345678": "Send_data",
    "87654321-4321-9876-5432-123456789012": "Receive_data"
}

# Storage for discovered handles
handle_map = {}  # handle -> {uuid, meaning}
uuid_map = {}    # uuid -> handle

async def main():
    # Replace with your peripheral's address
    address = "00:01:02:03:04:05"
    async with BleakClient(address) as client:
        print(f"Connected to {address}")

        # Discover services and characteristics
        services = await client.get_services()
        for service in services:
            for char in service.characteristics:
                uuid_str = str(char.uuid)
                if uuid_str in known_chars:
                    handle_map[char.handle] = {"uuid": uuid_str, "meaning": known_chars[uuid_str]}
                    uuid_map[uuid_str] = char.handle
                    print(f"Found {known_chars[uuid_str]}: handle {char.handle}")

        # Example: Write to Receive_data
        recv_uuid = next(u for u, m in known_chars.items() if m == "Receive_data")
        recv_handle = uuid_map[recv_uuid]
        await client.write_gatt_char(recv_handle, b"test")
        print(f"Wrote to Receive_data (handle {recv_handle})")

        # Example: Read from Send_data
        send_uuid = next(u for u, m in known_chars.items() if m == "Send_data")
        send_handle = uuid_map[send_uuid]
        value = await client.read_gatt_char(send_handle)
        print(f"Read from Send_data (handle {send_handle}): {value}")

        # Reverse lookup example (e.g., in a callback or event)
        handle = send_handle
        info = handle_map[handle]
        print(f"Handle {handle} is {info['meaning']} (UUID: {info['uuid']})")

# Run the async code
asyncio.run(main())