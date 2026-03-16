import jrcontrol
from netrunner import receiver 
import asyncio, logging, coloredlogs

log = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")

jrcontrol.load_settings()

receiver.SERVER_ADDRESS = jrcontrol.COMMON.get("netrunner", "http://localhost:4000") # get server add from config 

jrcontrol.load_star()

receiver.FUNCTIONS["LF_LOAD"] = jrcontrol.load
receiver.FUNCTIONS["LF_RUN"] = jrcontrol.run
receiver.FUNCTIONS["LF_CANCEL"] = jrcontrol.cancel

asyncio.run(receiver.main())
