
# Constants   
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_READ = const(0x0002)
_FLAG_WRITE = const(0x0004)
_FLAG_NOTIFY = const(0x0010)
_DESC_UUID = "00002901-0000-1000-8000-00805f9b34fb"

Service_UUID = "bb0a3fb1-dd96-4748-9225-633faf3ae192"
Char_UUID_map = [
    {"designation" :   "send_data",         "uuid" :   "11111111-0000-1000-8000-00805f9b34fb",  "flags" : _FLAG_NOTIFY, "descriptors" : {"uuid" : _DESC_UUID, "flags" : _FLAG_READ}},
    {"designation" :   "notification",      "uuid" :   "12345678-0000-1000-8000-00805f9b34fb",  "flags" : _FLAG_NOTIFY, "descriptors" : {"uuid" : _DESC_UUID, "flags" : _FLAG_READ}},
    {"designation" :   "receive_c",         "uuid" :   "22222222-0000-1000-8000-00805f9b34fb",  "flags" : _FLAG_WRITE , "descriptors" : {"uuid" : _DESC_UUID, "flags" : _FLAG_READ}}
    #{"designation" :   "notification",      "uuid" :   "23c584c6-91dd-4115-8e5a-3fb5d84253d6",  "flags" : _FLAG_NOTIFY},
    #{"designation" :   "send_data",         "uuid" :   "c1536c4a-eb2f-4f0a-ab7b-c56656e726b3",  "flags" : _FLAG_NOTIFY},
    #{"designation" :   "receive_c",         "uuid" :   "18f53ed4-aa97-4351-9980-94682dd794e2",  "flags" : _FLAG_WRITE}
    #{"designation" :   "notification",      "uuid" :   "23c584c6-91dd-4115-8e5a-3fb5d84253d6",  "flags" : _FLAG_NOTIFY, "descriptors" : {"uuid" : _DESC_UUID, "flags" : _FLAG_READ}},
    #{"designation" :   "send_data",         "uuid" :   "c1536c4a-eb2f-4f0a-ab7b-c56656e726b3",  "flags" : _FLAG_NOTIFY, "descriptors" : {"uuid" : _DESC_UUID, "flags" : _FLAG_READ}},
    #{"designation" :   "receive_c",         "uuid" :   "18f53ed4-aa97-4351-9980-94682dd794e2",  "flags" : _FLAG_WRITE,  "descriptors" : {"uuid" : _DESC_UUID, "flags" : _FLAG_READ}}
    #{"designation" :   "dummy_bug",         "uuid" :   "4e1293bb-290e-41e9-9f74-8a43d16eb884",  "flags" : _FLAG_READ,   "descriptors" : {"uuid" : _DESC_UUID, "flags" : _FLAG_READ}},
    #{"designation" :   "send_data",         "uuid" :   "c1536c4a-eb2f-4f0a-ab7b-c56656e726b3",  "flags" : _FLAG_NOTIFY, "descriptors" : {"uuid" : _DESC_UUID, "flags" : _FLAG_READ}},
    #{"designation" :   "receive_c",         "uuid" :   "18f53ed4-aa97-4351-9980-94682dd794e2",  "flags" : _FLAG_WRITE,  "descriptors" : {"uuid" : _DESC_UUID, "flags" : _FLAG_READ}}
    #{"designation" :   "dummy_bug",         "uuid" :   "4e1293bb-290e-41e9-9f74-8a43d16eb884",  "flags" : _FLAG_READ,   "descriptors" : {"uuid" : _DESC_UUID, "flags" : _FLAG_READ}},
    #{"designation" :   "Receive_Data",      "uuid" :   "4e1293bb-290e-41e9-9f74-8a43d16eb884"},
    #{"designation" :   "Respiratory_Rate",  "uuid" :   "23c584c6-91dd-4115-8e5a-3fb5d84253d6"},
    #{"designation" :   "ECG",               "uuid" :   "cfe50de4-9783-4745-9cff-f67750a1ad6d"}
]


NAME = "ECMOSensor"