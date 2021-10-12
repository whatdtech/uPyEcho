from micropython import const
from machine import Pin

# from bluetooth.advertisement import Advertisement
# from threading.message import Message
from ble_advertising import advertising_payload
# from advertising_payload import Advertisement
from message import Message

# import uasyncio
import ubluetooth

from utime import ticks_us, ticks_diff
# from utime import ticks_diff

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)
_IRQ_GATTS_INDICATE_DONE = const(20)
_IRQ_MTU_EXCHANGED = const(21)
_IRQ_L2CAP_ACCEPT = const(22)
_IRQ_L2CAP_CONNECT = const(23)
_IRQ_L2CAP_DISCONNECT = const(24)
_IRQ_L2CAP_RECV = const(25)
_IRQ_L2CAP_SEND_READY = const(26)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)
_FLAG_BROADCAST = const(0x0001)
_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_INDICATE = const(0x0020)
# _FLAG_BROADCAST = const(0x0001)

_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)

# __CSC_SERVICE_UUID = ubluetooth.UUID(0x1816)

# __CSC_MEASUREMENT_CHAR_UUID = (
#     ubluetooth.UUID(0x2A5B),
#     ubluetooth.FLAG_NOTIFY,
# )

# __CSC_FEATURE_CHAR_UUID = (
#     ubluetooth.UUID(0x2A5C),
#     ubluetooth.FLAG_READ,
# )

__CSC_SERVICE_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")

__CSC_MEASUREMENT_CHAR_UUID = (
    ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    ubluetooth.FLAG_NOTIFY | ubluetooth.FLAG_WRITE,
)

__CSC_FEATURE_CHAR_UUID = (
    ubluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    ubluetooth.FLAG_READ | ubluetooth.FLAG_WRITE,
)

__CSC_SERVICE = (
    __CSC_SERVICE_UUID,
    (__CSC_MEASUREMENT_CHAR_UUID, __CSC_FEATURE_CHAR_UUID),
)



class CSCDevice:
    def __init__(self, name, wheel_pin, crank_pin, data, rxbuf=100):
        self._ble = ubluetooth.BLE()
        self._ble.active(True)
        self._ble.config('mac')
        self.__name = name
        self.__data = data
        self._ble.irq(self._irq)
        # ((self._time_handle,), (self._date_handle,), (self._tx_handle, self._rx_handle,),) = self._ble.gatts_register_services(
        #     (_SERVICES)
        # )
        ((self._measurement, self._feature),) = self._ble.gatts_register_services((__CSC_SERVICE,))
        # Increase the size of the rx buffer and enable append mode.
        self._ble.gatts_set_buffer(self._feature, rxbuf, True)
        self._connections = set()
        self.connected = Message()
        self._rx_buffer = bytearray()
        self._handler = None
        self.__notify_task = None

        self.__wheel_revolutions = 0
        self.__ticks_last_wheel_event = None

        self.__crank_revolutions = 0
        self.__ticks_last_crank_event = None
        # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
        self._payload = advertising_payload(name=name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._resp_data = advertising_payload(name='hello', appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._advertise()
        # wheel_pin.irq(self.__on_wheel_rotation, Pin.IRQ_FALLING)
        # crank_pin.irq(self.__on_crank_rotation, Pin.IRQ_FALLING)

    def irq(self, handler):
        self._handler = handler

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            #s.close()
            # latch = 0
            print('connected BLE device')
            conn_handle, _, _, = data
            self._connections.add(conn_handle)
            self.connected.set()
        elif event == _IRQ_CENTRAL_DISCONNECT:
            # latch = 1
            print('BLE device disconnected')
            conn_handle, _, _, = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            self.connected.clear()
            # Start advertising again to allow a new connection.
            self._advertise()
            #s.listen(5)
        elif event == _IRQ_GATTS_WRITE:
            print('BLE WRITE PROTOCOL')
            conn_handle, value_handle, = data
            if conn_handle in self._connections and value_handle == self._feature:
                self._rx_buffer += self._ble.gatts_read(self._feature)
                if self._handler:
                    self._handler()
        elif event == _IRQ_SCAN_RESULT:
            print('BLE SCAN RESULT')
            addr_type, addr, iscon, rssi, adv_data = data
            if iscon:
                print('type:{} addr:{} rssi:{} data:{}'.format(addr_type, ubinascii.hexlify(addr), rssi, ubinascii.hexlify(adv_data)))
        elif event == _IRQ_SCAN_DONE:
            print('BLE SCAN Done')
        elif event == _IRQ_GATTS_READ_REQUEST:
            print('_IRQ_GATTS_READ_REQUEST')
        elif event == _IRQ_GATTC_SERVICE_RESULT:
            print('_IRQ_GATTC_SERVICE_RESULT')
        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            print('_IRQ_GATTC_CHARACTERISTIC_RESULT')
        elif event == _IRQ_GATTC_DESCRIPTOR_RESULT:
            print('_IRQ_GATTC_DESCRIPTOR_RESULT')
        elif event == _IRQ_GATTC_NOTIFY:
            print('_IRQ_GATTC_NOTIFY')
        elif event == _IRQ_GATTC_READ_DONE:
            print('_IRQ_GATTC_READ_DONE')
        elif event == _IRQ_GATTC_WRITE_DONE:
            print('_IRQ_GATTC_WRITE_DONE')
        elif event == _IRQ_GATTC_INDICATE:
            print('_IRQ_GATTC_INDICATE')
        elif event == _IRQ_GATTC_INDICATE:
            print('_IRQ_GATTC_INDICATE')
        elif event == _IRQ_GATTS_INDICATE_DONE:
            print('_IRQ_GATTS_INDICATE_DONE')
        elif event == _IRQ_MTU_EXCHANGED:
            print('_IRQ_MTU_EXCHANGED')
        elif event == _IRQ_GATTC_SERVICE_DONE:
            print('_IRQ_GATTC_SERVICE_DONE')
        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            print('_IRQ_GATTC_CHARACTERISTIC_DONE')
        elif event == _IRQ_GATTC_DESCRIPTOR_DONE:
            print('_IRQ_GATTC_DESCRIPTOR_DONE')
        elif event == _IRQ_GATTC_READ_RESULT:
            print('_IRQ_GATTC_READ_RESULT')
        elif event == _IRQ_PERIPHERAL_CONNECT:
            print('_IRQ_PERIPHERAL_CONNECT')
        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            print('_IRQ_PERIPHERAL_DISCONNECT')
        else :
            print('BLE none event: ', event)
            #latch = 1
            #s.listen(5)

    def any(self):
        return len(self._rx_buffer)

    def read(self, sz=None):
        if not sz:
            sz = len(self._rx_buffer)
        result = self._rx_buffer[0:sz]
        self._rx_buffer = self._rx_buffer[sz:]
        return result
    # def readtime(self):
    #     for conn_handle in self._connections:
    #         self._ble.gatts_read(self._time_handle)
    # def readdate(self):
    #     for conn_handle in self._connections:
    #         self._ble.gatts_read(self._date_handle)
    def notif(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._measurement, data)
    def write(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_write(self._measurement, data)
    # def writegatts(self, data):
    #     for conn_handle in self._connections:
    #         self._ble.gatts_write(self._tx_handle, data)

    def close(self):
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
        self._connections.clear()

    def _advertise(self, interval_us=150000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload, resp_data=self._resp_data, connectable=True)
        print('payload is:')
        print(self._payload)
    def _scan(self, interval_us=1280000):
        self._ble.gap_scan(None, interval_us, window_us=11250, active=False)
        print('payload is:')
        print(self._payload)