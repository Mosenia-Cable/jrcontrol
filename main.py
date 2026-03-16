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

def refresh_configs(interval=1200): # every 20 minutes by default
    while True:
        time.sleep(interval)
        log.info(f"Refreshing Jr configuration and common.json.")
        jrcontrol.load_settings()
        jrcontrol.load_star()

receiver.threading.Thread(target=refresh_configs, daemon=True).start() # wretched but idgaf

asyncio.run(receiver.main())