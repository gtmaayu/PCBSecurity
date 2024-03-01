from . import test2m as relaylib

def init():
    relaylib.loadLib()
    relaylib.getLibFunctions()
    relaylib.enumDevs()
    try:
        relaylib.openDevById(relaylib.devids[0])
    except IndexError:
        raise OSError("No relay found")
    
def on():
    relaylib.L.usb_relay_device_open_one_relay_channel(relaylib.hdev, 1)
    
def off():
    relaylib.L.usb_relay_device_close_one_relay_channel(relaylib.hdev, 1)

def close():
    relaylib.closeDev()
    relaylib.unloadLib()