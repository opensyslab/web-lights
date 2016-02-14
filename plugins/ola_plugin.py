import array
dummy_mode = False
try:
    from ola.ClientWrapper import ClientWrapper
except ImportError:
    dummy_mode = True
    
from plugins.server_plugin import ServerPlugin

UNIVERSE = 1
SEGMENTS = 8
COLORS = 3
MAX_CHANNELS = 512

ATTR_RED = 'r'
ATTR_GREEN = 'g'
ATTR_BLUE = 'b'

MODE_SOLID = 0
MODE_PULSE = 1

TICK_INTERVAL = 100

wrapper = None
instance = None
tick = 0

class OlaPlugin(ServerPlugin):

    ## PLUGIN METHODS ##

    def _on_init_plugin(self):
        
        # set instance
        global instance
        instance = self
            
        # mode
        self.mode = MODE_SOLID
        
        # restore state
        self._restore_state()
        
        # start render loop
        if not dummy_mode:
            start_loop()
        
    def do(self,data):
        
        # save state
        self.state = data
        
        # persist state
        self._save_state()
        
    def _tick(self):
        if self.mode == MODE_SOLID:
            pass
        elif self.mode == MODE_PULSE:
            phase = tick / 255
            self.state[ATTR_RED][0] = int(self.state[ATTR_RED][0]*phase)
            self.state[ATTR_GREEN][0] = int(self.state[ATTR_GREEN][0]*phase)
            self.state[ATTR_BLUE][0] = int(self.state[ATTR_BLUE][0]*phase)
        
        global tick
        tick = (tick + 1) % 255

    def get_color(self):
        return ( int(self.state[ATTR_RED][0]), int(self.state[ATTR_GREEN][0]), int(self.state[ATTR_BLUE][0]) )

## OLA METHODS ##

def stop_wrapper(state):
    if not state.Succeeded():
        wrapper.Stop()
        
def start_loop():
    global wrapper
    wrapper = ClientWrapper()
    wrapper.AddEvent(TICK_INTERVAL, update_color)
    wrapper.Run()

def update_color():
    
    # Schedule tick
    wrapper.AddEvent(TICK_INTERVAL, update_color)

    # Get next color
    r,g,b = instance.get_color()
    instance._tick()
    
    # Fill RGB bar array
    data = array.array('B')
    for i in range(0,SEGMENTS):
        data.append(r)
        data.append(g)
        data.append(b)

    # Fill remaining channels with zeros
    for i in range(0,MAX_CHANNELS-SEGMENTS*COLORS):
        data.append(0)

    # send
    if wrapper:
        wrapper.Client().SendDmx(UNIVERSE, data, stop_wrapper)



if __name__=="__main__":
    o = OlaPlugin()
