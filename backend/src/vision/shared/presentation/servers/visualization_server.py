import sys, traceback, Ice
import logging

class VisualServer:
    def __init__(self, visualizer):
        self.logger = logging.getLogger()
        self.visualizer = visualizer
        self.endpoint = "default -h 0.0.0.0 -p 9957:ws -h 0.0.0.0 -p 12000"
        self.logger.info("Connect: " + self.endpoint)
        id = Ice.InitializationData()
        self.ic = Ice.initialize(None, id)
        self.adapter = self.ic.createObjectAdapterWithEndpoints("3DVizA", self.endpoint)
        self.logger.info(self.adapter)

    def run(self):
        try:
            self.adapter.add(self.visualizer, self.ic.stringToIdentity("3DViz"))
            self.adapter.activate()
            self.ic.waitForShutdown()
        except KeyboardInterrupt:
            del self.ic
            sys.exit()