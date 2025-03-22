from micropython import const
import time
from communication import Communication


_CMD_TIMEOUT = const(100)

_R1_IDLE_STATE = const(1 << 0)
# R1_ERASE_RESET = const(1 << 1)
_R1_ILLEGAL_COMMAND = const(1 << 2)
# R1_COM_CRC_ERROR = const(1 << 3)
# R1_ERASE_SEQUENCE_ERROR = const(1 << 4)
# R1_ADDRESS_ERROR = const(1 << 5)
# R1_PARAMETER_ERROR = const(1 << 6)
_TOKEN_CMD25 = const(0xFC)
_TOKEN_STOP_TRAN = const(0xFD)
_TOKEN_DATA = const(0xFE)


class SDCard:
    def __init__(self, spi, cs, baudrate=1320000, debug=False):
        self.debug = debug # debug printing
        self.print(f"Initializing SD card")
        
        self.spi = spi
        self.cs = cs
        self.baudrate = baudrate

        self.cmdbuf = bytearray(6)
        self.dummybuf = bytearray(512)
        self.tokenbuf = bytearray(1)
        for i in range(512):
            self.dummybuf[i] = 0xFF
        self.dummybuf_memoryview = memoryview(self.dummybuf)

        # Before initializing the card
        self.init_mode = True

        # initialise the card
        self.init_card(self.baudrate)

    def init_spi(self, baudrate):
        self.spi.init(baudrate=baudrate, phase=0, polarity=0)

    def init_card(self, baudrate):
        # Configure SPI bus with appropriate clock speed (slow initially)
        # Set chip select (CS) pin high to deselect card
        # Send at least 74 clock cycles with CS high
        # CMD0 - R1 response, 1 byte - 1
        # CMD8 - R7 response, 5 bytes - 1 = v2 card; 5 = v1 card (error)
        # for v2 cards:
            # CMD 58 - R3 response, 5 bytes
            # CMD 55 - R1 response, 1 byte
            # ACMD41 (CMD55 + CMD 41) - R1 response, 1 byte
        # for v1 cards:
            # ACMD41 - R1 response, 1 byte
        # CMD58 - R3 response, 5 bytes
        # CMD9 - R1 response, 1 byte
        # CMD16 - R1 response, 1 byte

        # init CS pin
        self.cs.init(self.cs.OUT, value=1)

        # init SPI bus; use low data rate for initialisation
        self.init_spi(100000)

        # clock card at least 100 cycles with cs high
        for i in range(16):
            self.spi.write(b"\xff")

        # CMD0: init card; should return _R1_IDLE_STATE (allow 5 attempts)
        try:
            for _ in range(5):
                if self.cmd(0, 0, 0x95)[0] == _R1_IDLE_STATE:
                    break
            else:
                raise OSError()
        except:
            raise OSError("no SD card")

        # CMD8: determine card version
        try:
            r = self.cmd(8, 0x01AA, 0x87, readbytes=5)[0]
            if r == _R1_IDLE_STATE:
                self.init_card_v2()
            elif r == (_R1_IDLE_STATE | _R1_ILLEGAL_COMMAND):
                self.init_card_v1()
            else:
                raise OSError()
        except:
            raise OSError("couldn't determine SD card version")

        # get the number of sectors
        # CMD9: response R2 (R1 byte + 16-byte block read + 2 bytes CRC)
        try:
            if self.cmd(9, 0, 0xff, release=False)[0] != 0:
                raise OSError()
        except:
            raise OSError("no response from SD card")
        csd = bytearray(16)
        self.readinto(csd)
        self.print(f"CSD: {csd}")
        if csd[0] & 0xC0 == 0x40:  # CSD version 2.0
            #self.sectors = ((csd[8] << 8 | csd[9]) + 1) * 1024
            c_size = (csd[7] & 0x3F) << 16 | csd[8] << 8 | csd[9]
            self.sectors = (c_size + 1) * 1024
        elif csd[0] & 0xC0 == 0x00:  # CSD version 1.0 (old, <=2GB)
            c_size = (csd[6] & 0b11) << 10 | csd[7] << 2 | csd[8] >> 6
            c_size_mult = (csd[9] & 0b11) << 1 | csd[10] >> 7
            read_bl_len = csd[5] & 0b1111
            capacity = (c_size + 1) * (2 ** (c_size_mult + 2)) * (2**read_bl_len)
            self.sectors = capacity // 512
        else:
            raise OSError("SD card CSD format not supported")
        # print('sectors', self.sectors)

        # CMD16: set block length to 512 bytes
        try:
            if self.cmd(16, 512, 0xff)[0] != 0:
                raise OSError()
        except:
            raise OSError("can't set 512 block size")

        self.init_mode = False

    def init_card_v1(self):
        for i in range(_CMD_TIMEOUT):
            time.sleep_ms(50)
            self.cmd(55, 0, 0xff)
            if self.cmd(41, 0, 0xff)[0] == 0:
                # SDSC card, uses byte addressing in read/write/erase commands
                self.cdv = 512
                # print("[SDCard] v1 card")
                return
        raise OSError("timeout waiting for v1 card")

    def init_card_v2(self):
        time.sleep_ms(50)
        self.cmd(58, 0, 0xff, readbytes=5)

        for i in range(_CMD_TIMEOUT):
            time.sleep_ms(50)

            self.cmd(55, 0x00000000, 0xff)
            acmd41_response = self.cmd(41, 0x40100000, 0xff)[0]
            if acmd41_response == 0:
                ocr_response = self.cmd(58, 0, 0xff, readbytes=5)
                if ocr_response[0] == 0:
                    if ocr_response[1] & 0x80:
                        # SDHC/SDXC card, uses block addressing in read/write/erase commands
                        self.cdv = 1
                    else:
                        # SDSC card, uses byte addressing in read/write/erase commands
                        self.cdv = 512
                    # print("[SDCard] v2 card")
                    return
        raise OSError("timeout waiting for v2 card")

    def cmd(self, cmd, arg, crc, release=True, readbytes=1):
        self.cs(0)
        self.check_spi_config()

        # create and send the command
        buf = self.cmdbuf
        buf[0] = 0x40 | cmd
        buf[1] = arg >> 24
        buf[2] = arg >> 16
        buf[3] = arg >> 8
        buf[4] = arg
        buf[5] = crc
        self.spi.write(buf)
        
        # Wait for valid response (bit 7 == 0)
        collected_tokens = []
        
        # First wait for valid response
        for i in range(_CMD_TIMEOUT):
            token = bytearray(1)
            self.spi.readinto(token, 0xFF)
            if not (token[0] & 0x80):  # Valid response found
                collected_tokens.append(token[0])
                break
        else:
            # Timeout occurred
            self.cs(1)
            self.spi.write(b"\xff")
            self.print("CMD timeout, no valid response")
            return -1
        
        # Read remaining bytes after valid response
        for j in range(readbytes - 1):
            token = bytearray(1)
            self.spi.readinto(token, 0xFF)
            collected_tokens.append(token[0])
        
        # Release chip select if requested
        if release:
            self.cs(1)
            self.spi.write(b"\xff")
        
        self.print(f"CMD{cmd} response: {collected_tokens}")
        return collected_tokens

    def readinto(self, buf):
        self.cs(0)
        self.check_spi_config()

        # read until start byte (0xFE)
        for i in range(_CMD_TIMEOUT):
            self.spi.readinto(self.tokenbuf, 0xFF)
            if self.tokenbuf[0] == _TOKEN_DATA:
                break
            #time.sleep_ms(1)
        else:
            self.cs(1)
            raise OSError("timeout waiting for response")

        # read data
        mv = self.dummybuf_memoryview
        if len(buf) != len(mv):
            mv = mv[: len(buf)]
        self.spi.write_readinto(mv, buf)

        # read checksum
        self.spi.write(b"\xff")
        self.spi.write(b"\xff")

        self.cs(1)
        self.spi.write(b"\xff")

    def write(self, token, buf):
        self.cs(0)
        self.check_spi_config()

        # send: start of block, data, checksum
        self.spi.read(1, token)
        self.spi.write(buf)
        self.spi.write(b"\xff")
        self.spi.write(b"\xff")

        # check the response
        if (self.spi.read(1, 0xFF)[0] & 0x1F) != 0x05:
            self.cs(1)
            self.spi.write(b"\xff")
            return

        # wait for write to finish
        while self.spi.read(1, 0xFF)[0] == 0:
            pass

        self.cs(1)
        self.spi.write(b"\xff")

    def write_token(self, token):
        self.cs(0)
        self.check_spi_config()
        
        self.spi.read(1, token)
        self.spi.write(b"\xff")
        # wait for write to finish
        while self.spi.read(1, 0xFF)[0] == 0x00:
            pass

        self.cs(1)
        self.spi.write(b"\xff")

    def readblocks(self, block_num, buf):
        self.check_spi_config()
        
        # workaround for shared bus, required for (at least) some Kingston
        # devices, ensure MOSI is high before starting transaction
        self.spi.write(b"\xff")

        nblocks = len(buf) // 512
        assert nblocks and not len(buf) % 512, "Buffer length is invalid"
        if nblocks == 1:
            # CMD17: set read address for single block
            if self.cmd(17, block_num * self.cdv, 0xff, release=False)[0] != 0:
                # release the card
                self.cs(1)
                raise OSError(5)  # EIO
            # receive the data and release card
            self.readinto(buf)
        else:
            # CMD18: set read address for multiple blocks
            if self.cmd(18, block_num * self.cdv, 0xff, release=False)[0] != 0:
                # release the card
                self.cs(1)
                raise OSError(5)  # EIO
            offset = 0
            mv = memoryview(buf)
            while nblocks:
                # receive the data and release card
                self.readinto(mv[offset : offset + 512])
                offset += 512
                nblocks -= 1
            try:    
                if self.cmd(12, 0, 0xFF, readbytes=2)[1]:
                    raise OSError()  # EIO
            except:
                raise OSError(5)  # EIO

    def writeblocks(self, block_num, buf):
        self.check_spi_config()

        # workaround for shared bus, required for (at least) some Kingston
        # devices, ensure MOSI is high before starting transaction
        self.spi.write(b"\xff")

        nblocks, err = divmod(len(buf), 512)
        assert nblocks and not err, "Buffer length is invalid"
        if nblocks == 1:
            # CMD24: set write address for single block
            if self.cmd(24, block_num * self.cdv, 0xff)[0] != 0:
                raise OSError(5)  # EIO

            # send the data
            self.write(_TOKEN_DATA, buf)
        else:
            # CMD25: set write address for first block
            if self.cmd(25, block_num * self.cdv, 0xff)[0] != 0:
                raise OSError(5)  # EIO
            # send the data
            offset = 0
            mv = memoryview(buf)
            while nblocks:
                self.write(_TOKEN_CMD25, mv[offset : offset + 512])
                offset += 512
                nblocks -= 1
            self.write_token(_TOKEN_STOP_TRAN)

    def ioctl(self, op, arg):
        if op == 4:  # get number of blocks
            return self.sectors
        if op == 5:  # get block size in bytes
            return 512
    
    def print(self, *args, **kwargs): # Debug print function for SD card operations.
        if hasattr(self, 'debug') and self.debug:
            prefix = "[SDCard] "
            if args:
                # Convert first argument to string and prepend prefix
                args = (prefix + str(args[0]),) + args[1:]
            else:
                args = (prefix,)
            
            # Use standard print function with all passed arguments and kwargs
            print(*args, **kwargs)
        # Silently ignore if debug is disabled
    
    def check_spi_config(self):
        """
        Check if SPI is configured correctly for SD card.
        If not, update the stored SPI configuration and reinitialize the bus.
        
        Args:
            init_mode: Boolean indicating if we're in initialization mode (which uses 100000 baudrate)
        """
        # Get the communication singleton's stored SPI config
        comm = Communication()
        spi_config = comm.spi_config
        
        # Determine which baudrate to use
        target_baudrate = 100000 if self.init_mode else self.baudrate
        
        # Check if current config differs from what SD card needs
        if (spi_config.get("baudrate") != target_baudrate or 
            spi_config.get("phase") != 0 or 
            spi_config.get("polarity") != 0):
            
            # Update the stored config values
            comm.spi_config = {"baudrate": target_baudrate, "phase": 0, "polarity": 0}
            
            # Actually reinitialize the SPI bus with our needed parameters
            self.init_spi(target_baudrate)
            self.print(f"SPI reconfigured for SD card (baudrate={target_baudrate})")
    
    