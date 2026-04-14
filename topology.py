# Import Topo base class from Mininet
from mininet.topo import Topo


# Create custom topology class
class PathTopo(Topo):

    # Build topology structure
    def build(self):

        # Add two hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # Add three switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Create links between hosts and switches
        self.addLink(h1, s1)
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, h2)


# Expose topology name for Mininet command line usage
topos = {'mypath': PathTopo}
