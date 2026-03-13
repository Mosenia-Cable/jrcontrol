import jrcontrol
from netrunner import receiver 
import asyncio, logging, coloredlogs

log = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")

jrcontrol.load_settings()
jrcontrol.load_star()

receiver.FUNCTIONS["LF_LOAD"] = jrcontrol.load
receiver.FUNCTIONS["LF_RUN"] = jrcontrol.run
receiver.FUNCTIONS["LF_CANCEL"] = jrcontrol.cancel

asyncio.run(receiver.main())
