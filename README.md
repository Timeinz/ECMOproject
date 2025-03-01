Project Dependency Hierarchy

This project uses a modular dependency hierarchy to manage hardware interactions:

    config: Defines hardware pin assignments (e.g., I2C_SCL, I2C_SDA).
    communication: Initializes communication protocols (SPI, Bluetooth, I2C) using config pins.
    printhandler: Handles messaging and communication, relying on communication.
    peripherals: Manages devices (ADC, RTC, SD Card, etc.), using printhandler and communication.

The structure ensures loose coupling—each module depends on the one below it via simple interfaces, keeping them independent and maintainable.
Flowchart

+----------------+       +----------------+       +----------------+       +----------------+
|   peripherals  | ----> |  printhandler  | ----> |  communication | ----> |     config     |
| (ADC, RTC, SD) |       |  (messaging)   |       | (SPI, BT, I2C) |       |  (HW pins)     |
+----------------+       +----------------+       +----------------+       +----------------+

    Direction: Arrows show dependency flow (e.g., peripherals calls printhandler).
    Purpose: Separates concerns for clarity and scalability in an embedded system.
