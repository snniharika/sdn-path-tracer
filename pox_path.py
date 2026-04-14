from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()
mac_to_port = {}

def install_flow(connection, in_port, dst, out_port):
    msg = of.ofp_flow_mod()
    msg.match.in_port = in_port
    msg.match.dl_dst = dst
    msg.actions.append(of.ofp_action_output(port=out_port))
    connection.send(msg)

def _handle_PacketIn(event):
    packet = event.parsed
    if not packet.parsed:
        return

    src = packet.src
    dst = packet.dst
    dpid = event.connection.dpid
    in_port = event.port

    if dpid not in mac_to_port:
        mac_to_port[dpid] = {}

    mac_to_port[dpid][src] = in_port

    if dst in mac_to_port[dpid]:
        out_port = mac_to_port[dpid][dst]
        install_flow(event.connection, in_port, dst, out_port)
    else:
        out_port = of.OFPP_FLOOD

    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.in_port = in_port
    msg.actions.append(of.ofp_action_output(port=out_port))
    event.connection.send(msg)

    log.info("Packet at s%s | %s -> %s | in=%s out=%s",
             dpid, src, dst, in_port, out_port)

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("POX Path Tracer Controller Started")
