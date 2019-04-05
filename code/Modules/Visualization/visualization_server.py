import sys, traceback, Ice

class VisualServer:
    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.endpoint = "default -h localhost -p 9957:ws -h localhost -p 11000"
        print("Connect: " + self.endpoint)
        id = Ice.InitializationData()
        self.ic = Ice.initialize(None, id)
        self.adapter = self.ic.createObjectAdapterWithEndpoints("3DVizA", self.endpoint)

    def run(self):
        try:
            self.adapter.add(self.visualizer, self.ic.stringToIdentity("3DViz"))
            self.adapter.activate()
        except KeyboardInterrupt:
            del self.ic
            sys.exit()