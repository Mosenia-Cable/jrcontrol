import os, sys, json, requests, time
import logging
PROGRAM_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROGRAM_PATH)

log = logging.getLogger(__name__)

COMMON = {}
STAR_CFG = {}
STAR_FLAVORS = {}
PRESENTATIONS = {}

def load_settings():
    '''Loads common.json dictionary'''
    global COMMON
    common_path = os.path.join(PROGRAM_PATH, "common.json")
    if os.path.exists(common_path):
        try:
            with open(common_path, "r") as common_f:
                COMMON = json.load(common_f)
                common_f.close()
            log.info(f"Loaded common settings from {common_path}")
        except json.JSONDecodeError:
            log.error(f"Malformed JSON in {common_path}.")
        except: 
            log.error(f"Unhandled exception attempting to access {common_path}.", exc_info=True)

def load_star():
    global COMMON
    global STAR_CFG
    global STAR_FLAVORS
    '''Load the config and flavors from the JrEncoder.'''
    jr_conn = COMMON.get("conn", "http://localhost:5000")
    endpoint = "/config/get"
    request_url = jr_conn.rstrip("/") + endpoint
    r = requests.get(request_url, timeout=10)
    if r.status_code == 200:
        try:
            data = r.json()
            STAR_CFG = data.get("config", {})
            STAR_FLAVORS = data.get("flavors", {}).get("Flavor", [])
            log.info(f"Successfully retrieved configuration and flavors from {jr_conn}")
        except requests.exceptions.JSONDecodeError:
            log.error(f"JrEncoder did not return a valid JSON response.")
        except:
            log.error(f"Unhandled exception while trying to fetch JrEncoder config.", exc_info=True)
    else:
        log.error(f"Failed to request {request_url}, status code {r.status_code}")

def send_alert(text:str="Default String", mode:str="Warning", **kwargs):
    if mode not in ["Warning", "Advisory"]:
        log.error(f"Bad alert mode: {mode}.")
    else:
        global COMMON
        jr_conn = COMMON.get("conn", "http://localhost:5000")
        endpoint = "/alert/send"
        request_data = {'text': text, 'type': mode}
        request_url = jr_conn.rstrip("/") + endpoint
        requests.post(request_url, data=request_data, timeout=10)

def cancel(pres_id:str, **kwargs):
    '''Cancels the active presentation and removes a loaded pres_id from the bank, if provided.'''
    global COMMON
    global PRESENTATIONS
    jr_conn = COMMON.get("conn", "http://localhost:5000")
    endpoint = "/presentation/cancel"
    request_url = jr_conn.rstrip("/") + endpoint
    r = requests.post(request_url, timeout=10)
    if r.status_code == 200:
        log.info("Successfully cancelled the active presentation.")
    else:
        log.error(f"Failed to request {request_url}, status code {r.status_code}.")
    
    ## delete loaded from bank if a not-yet-running presentation is cancelled before it's run
    if pres_id:
        if PRESENTATIONS.get(pres_id, None) != None: # only try to pop if loaded into bank (not run yet)
            PRESENTATIONS.pop(pres_id) # popper

def load(pres_id:str, flav_name:str, flav_length:float, **kwargs):
    '''Load a presentation into the bank, in preparation for run.'''
    # First, let's try to derive an alias for the provided flav_name
    global COMMON
    # In common.json, you can define an alias name for a flavor. For example, 4comm will have "LDL1" and "LDL2" which we can map to different flavors specific to the jrencoder.
    aliases = COMMON.get("flavor_alias", {})
    alias = aliases.get(flav_name, None)
    if alias:
        log.debug(f"Called flavor '{flav_name}' has an alias of '{alias}'")
        flav_name = alias # flav_name is what will be used
    # now we'll index to find if the flavor called actually exists
    flavor = None
    global STAR_FLAVORS
    for f in STAR_FLAVORS:
        # find by indexing
        if f.get("Name") == flav_name: # keep in mind this is case sensitive
            flavor = f
            log.debug(f"Got valid flavor '{flav_name}'")
            break
    if flavor:
        global PRESENTATIONS
        PRESENTATIONS[pres_id] = flav_name
        log.info(f"Presentation {pres_id} loaded as flavor '{flav_name}'")
    else:
        log.warning(f"Presentation {pres_id} not loaded: no flavor is defined for called name '{flav_name}'")

def run(pres_id:str, ts:float=0, **kwargs):
    '''Run a loaded presentation at the defined epoch timestamp. If undefined, run immediately.'''
    global PRESENTATIONS
    flavor = PRESENTATIONS.get(pres_id, None)

    ts = round(ts, 2) # jrencoder API only takes floats within an abstract decimal length
    log.debug(f"Desired run time: {ts}")
    retry_count = 0
    if not flavor:
        # if for some reason the RUN is sent faster than the LOAD, we can retry up to 5 times
        while not flavor and retry_count < 5: 
            log.warning(f"No flavor loaded matching ID {pres_id}! Trying again... ({retry_count + 1})")
            flavor = PRESENTATIONS.get(pres_id, None)
            retry_count += 1
            time.sleep(0.25)

    if flavor:
        global COMMON
        jr_conn = COMMON.get("conn", "http://localhost:5000")
        loop_flavors = COMMON.get("loop_flavors", [])
        if flavor in loop_flavors:
            endpoint = "/presentation/loop"
        else: endpoint = "/presentation/run"
        request_url = jr_conn.rstrip("/") + endpoint
        request_data = {"flavor": flavor, "time": int(ts)}
        log.debug(request_data)
        r = requests.post(request_url, timeout=10, data=request_data)
        if r.status_code == 200:
            log.info(f"Successfully requested to run presentation {pres_id} (flavor {flavor}).")
        else:
            log.error(f"Failed to request {request_url}, status code {r.status_code}.")
        PRESENTATIONS.pop(pres_id) # clear the presentation from the bank so it isn't re-run if the same ID happens to be called
    else:
        log.warning(f"Failed to run {pres_id}, no flavor loaded matching the ID.")
        



if __name__ == "__main__":
    import coloredlogs
    coloredlogs.install(level="DEBUG")
    load_settings()
    load_star()
    cancel(pres_id=1)
    load(pres_id=1,flav_name="G",flav_length=120)
    #load(pres_id="LDL1",flav_name="LDL1")
    time.sleep(1)
    run(pres_id=1,ts=0)