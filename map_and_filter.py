from netfilterqueue import NetfilterQueue
from scapy.all import *
from uuid import uuid4
from hexdump import hexdump

subscribers = {}

def str2arr(string):
    return list(map(lambda x: ord(x), list(string)))

def gen_id(length):
    # not really unique
    return str(uuid4())[:length]

def get_tcp(pkt):
    return IP(pkt.get_payload()).payload

def gen_mqtt_topic(pkt, tp):
    mqtt = get_mqtt_pkt(pkt) 
    # not exactly, length is byte4 + byte5
    length = mqtt[tp - 1]
    key = gen_id(length)
    return key

def get_mqtt_pkt(pkt):
    ip = IP(pkt.get_payload())
    mqtt = raw(ip.payload.payload) 
    return mqtt

def get_mqtt_topic(pkt, tp):
    mqtt = get_mqtt_pkt(pkt) 
    length = mqtt[tp - 1] 
    topic = mqtt[tp : tp + length]
    return topic

def dump_mqtt_pkt(pkt):
    mqtt = get_mqtt_pkt(pkt) 
    print(mqtt)
    hexdump(mqtt) 

def get_control_code(pkt):
    mqtt = get_mqtt_pkt(pkt) 
    if mqtt:
        return mqtt[0] >> 4
    else:
        return None

def set_mqtt_pkt(pkt, l_mqtt):
    ip = IP(pkt.get_payload())
    ip.payload.payload = Raw(bytes(l_mqtt))
    del ip.payload.chksum
    del ip.chksum
    del ip.len 
    new_ip = IP(ip.build())
    pkt.set_payload(raw(new_ip))

def replace_topic(pkt, new_topic, tp):
    mqtt = get_mqtt_pkt(pkt)
    length = mqtt[tp - 1]
    l_mqtt = list(mqtt) 
    l_mqtt = l_mqtt[:tp] + str2arr(new_topic) + l_mqtt[tp + length :]
    if (new_topic == "test"):
        print("l_mqtt", l_mqtt)
    set_mqtt_pkt(pkt, l_mqtt)


def search_key(target):
    for key, topic in subscribers.items():
        if (topic == target):
            return key
    return None


def search_topic(target):
    for key, topic in subscribers.items():
        if (key == target):
            return topic
    return None

def map_sub_pkt(pkt):
    # topic filter position
    tp = 6
    topic = get_mqtt_topic(pkt, tp)
    key = search_key(topic)
    if key:
        replace_topic(pkt, key, tp)
        return 
    key = gen_mqtt_topic(pkt, tp) 
    replace_topic(pkt, key, tp)
    subscribers[key] = topic

def unmap_pub_pkt(pkt):
    tp = 4
    key = get_mqtt_topic(pkt, tp)
    topic = search_topic(key.decode("utf-8"))
    if topic:
        new_topic = topic.decode("utf-8")
        print("new topic", new_topic)
        replace_topic(pkt, new_topic, tp)

def map_pub_pkt(pkt):
    tp = 4
    topic = get_mqtt_topic(pkt, tp)
    key = search_key(topic)
    if key == None:
        print("can not find mapping topic", topic)
        # replace_topic(pkt, topic, tp)
    else:
        replace_topic(pkt, key, tp)

def unmap_ubsub_pkt(pkt):
    # TODO: remove key for the unsubscribbing topic
    hexdump(pkt)

def map_and_accept(pkt):
    control_code = get_control_code(pkt)
    if control_code == 8:
        # subscribe
        map_sub_pkt(pkt)     
    elif control_code == 10:
        # unsubscribe
        unmap_ubsub_pkt(pkt)
    elif control_code == 3:
        tcp = get_tcp(pkt)
        if tcp.dport == 1883:
            # publish from client
            map_pub_pkt(pkt)
        elif tcp.sport == 1883:
            # publish from broker
            unmap_pub_pkt(pkt)
        # else:
        #     unmap_pub_pkt(pkt)
    pkt.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, map_and_accept)
try:
    nfqueue.run()
except KeyboardInterrupt:
    print('')

nfqueue.unbind()
