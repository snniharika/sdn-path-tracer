# Import POX core module for controller services and logging
from pox.core import core

# Import OpenFlow 1.0 message library
import pox.openflow.libopenflow_01 as of

# Create logger object to print controller messages
log = core.getLogger()

# Dictionary to store MAC-to-port mapping for each switch
# Format: {dpid: {mac_address: port}}
mac_to_port = {}


# Function to install a flow rule in the switch
def install_flow(connection, in_port, dst, out_port):
    # Create a flow modification message
    msg = of.ofp_flow_mod()

    # Match packets coming from input port
    msg.match.in_port = in_port

    # Match destination MAC address
    msg.match.dl_dst = dst

    # Action: forward packet to output port
    msg.actions.append(of.ofp_action_output(port=out_port))

    # Send flow rule to switch
    connection.send(msg)


# Function triggered whenever switch sends PacketIn to controller
def _handle_PacketIn(event):
    # Parse received packet
    packet = event.parsed

    # If packet parsing failed, ignore it
    if not packet.parsed:
        return

    # Source MAC address
    src = packet.src

    # Destination MAC address
    dst = packet.dst

    # Switch ID (datapath ID)
    dpid = event.connection.dpid

    # Port where packet entered switch
    in_port = event.port

    # Create table for switch if not already present
    if dpid not in mac_to_port:
        mac_to_port[dpid] = {}

    # Learn source MAC and remember incoming port
    mac_to_port[dpid][src] = in_port

    # If destination already known, forward directly
    if dst in mac_to_port[dpid]:
        out_port = mac_to_port[dpid][dst]

        # Install rule for future packets
        install_flow(event.connection, in_port, dst, out_port)

    else:
        # If destination unknown, flood packet
        out_port = of.OFPP_FLOOD

    # Create packet-out message for current packet
    msg = of.ofp_packet_out()

    # Attach original packet data
    msg.data = event.ofp

    # Input port of received packet
    msg.in_port = in_port

    # Output action
    msg.actions.append(of.ofp_action_output(port=out_port))

    # Send packet to switch
    event.connection.send(msg)

    # Log packet path information
    log.info("Packet at s%s | %s -> %s | in=%s out=%s",
             dpid, src, dst, in_port, out_port)


# Launch function runs when POX module starts
def launch():
    # Register PacketIn event handler
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)

    # Startup log message
    log.info("POX Path Tracer Controller Started")
