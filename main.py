import jrcontrol
from netrunner import receiver 
import asyncio, logging, coloredlogs, time

log = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")

jrcontrol.load_settings()

receiver.SERVER_ADDRESS = jrcontrol.COMMON.get("netrunner", "http://localhost:4000") # get server add from config 

jrcontrol.load_star()

receiver.FUNCTIONS["LF_LOAD"] = jrcontrol.load
receiver.FUNCTIONS["LF_RUN"] = jrcontrol.run
receiver.FUNCTIONS["LF_CANCEL"] = jrcontrol.cancel

def do_nothing(**kwargs):
    '''It literally does nothing.'''
    pass

def refresh_configs(interval=1200): # every 20 minutes by default
    while True:
        log.info(f"Refreshing Jr configuration and common.json.")
        jrcontrol.load_settings()
        jrcontrol.load_star()
        if jrcontrol.COMMON.get("auto_ts_offset", False):
            receiver.FUNCTIONS["HEARTBEAT"] = jrcontrol.adjust_auto_offset # allow HEARTBEAT packets to adjust the automated offset
        else:
            receiver.FUNCTIONS["HEARTBEAT"] = do_nothing # this will get rid of the warnings that fuss no function is set
        time.sleep(interval) # moved the sleep down here so that we can refresh and set heartbeat response immediately upon startup

receiver.threading.Thread(target=refresh_configs, daemon=True).start() # wretched but idgaf

asyncio.run(receiver.main())