from pylsl import resolve_stream, StreamInlet
from bridge.lsl_holo_bridge import LslHoloBridge
from bridge.bridge_data_classes import BridgeStreamInfo, BYTE_CODE_FLOAT_TYPE

if __name__ == "__main__":
    # create inlet to which the bridge as to listen to
    while True:
        print("Resolve bridge inlet…")

        streams = resolve_stream('type', 'EEG')

        inlet = StreamInlet(resolve_stream('type', 'EEG')[0])
        bridge_stream_inlet_info = BridgeStreamInfo(name="EEG",
                                                    channel_count=65,
                                                    pkg_type_in_bytes=BYTE_CODE_FLOAT_TYPE)

        inlets = {bridge_stream_inlet_info: inlet}

        print("Configure server…")
        bridge = LslHoloBridge(port=10000, host='0.0.0.0', inlets=inlets, outlets={})

        bridge.run_bridge()

        print("Restarting bridge…")
