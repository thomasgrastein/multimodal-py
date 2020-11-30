import network
import uasyncio
from utime import sleep_ms
import usocket as socket
import uasyncio as asyncio

SSID = "Thomas - iPhone"
PW = "12345678"
SERVER_IP = "172.20.10.6"
PORT = 5678

class Network:
    def __init__(self, peripherals, start, on_loose):
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        self.peripherals = peripherals
        self.socket = None
        self.connected = False
        self.state = "WAITING"
        self.start = start
        self.on_loose = on_loose
        try:
            self.peripherals.oled.fill(0)
            self.peripherals.oled.text("Scanning...", 10, 10)
            self.peripherals.oled.show()
        except Exception as e:
            print(e)
        self.wifi = network.WLAN(network.STA_IF)
        self.wifi.active(True)
        self.wifi.connect(SSID, PW)
        while not self.connected:
            while self.wifi.status() == network.STAT_CONNECTING:
                sleep_ms(100)
            if self.wifi.isconnected():
                print("Connection established. My IP is " +
                      str(self.wifi.ifconfig()[0]))
                try:
                    self.peripherals.oled.fill(0)
                    self.peripherals.oled.text("Connected (AP)", 10, 10)
                    self.peripherals.oled.show()
                except Exception as e:
                    print(e)
                self.connected = True
                break
            status = self.wifi.status()
            if status == network.STAT_WRONG_PASSWORD:
                status = "WRONG PASSWORD"
            elif status == network.STAT_NO_AP_FOUND:
                status = "NETWORK '%s' NOT FOUND" % SSID
            else:
                status = "Status code %d" % status
            print("Connection failed: %s!" % status)
            return
        if self.wifi.config('mac') == b'$\n\xc4_\xfc\xe8':  # Server
            coro = asyncio.start_server(self.tcp_server, SERVER_IP, PORT)
            self.task = asyncio.create_task(coro)
        else:
            self.task = asyncio.create_task(self.tcp_client())

    async def tcp_client(self):
        while True:
            fut = asyncio.open_connection(SERVER_IP, PORT)
            try:
                reader, writer = await asyncio.wait_for(fut, timeout=3)
                break
            except Exception as e:
                print("Timeout, retrying", e)
        while True:
            message = self.state
            writer.write(message.encode())
            await writer.drain()
            data = await reader.read(100)
            other_state = data.decode()
            print(other_state)
            if other_state == "WON":
                self.on_loose()
                self.state = "LOOSE"
            elif other_state == "STARTED" and self.state != "STARTED" and self.state != "LOOSE":
                self.start()
            writer.close()
            await asyncio.sleep_ms(500)

    async def tcp_server(self, _, peer):
        while True:
            fut = peer.read(100)
            try:
                data = await asyncio.wait_for(fut, timeout=1)
                other_state = data.decode()
                print(other_state)
                if other_state == "WON":
                    self.on_loose()
                    self.state = "LOOSE"
                elif other_state == "STARTED" and self.state != "STARTED" and self.state != "LOOSE" and self.state != "WON":
                    self.start()
            except Exception as e:
                print("Timeout, skipping", e)
            message = self.state
            peer.write(message.encode())
            await peer.drain()
            await asyncio.sleep_ms(500)

    def set_won(self):
        self.state = "WON"
