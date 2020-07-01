import aiohttp
import asyncio
import aioconsole
import time
import socketio

sio = socketio.AsyncClient()
start_timer = None

SERVER_IP_ADDRESS = "localhost"
is_lxc_ready = False


# ARM RTM request body
RTM_REQ_JSON_BODY_INTEL = {
                            "type": "Virtual",
	                        "model": "qemu-system-x86_64",
                            "redpesk_image": "RedPesk-minimal-28_II-1.x86_64.raw.xz",
	                        "redpesk_image_link": "https://download.redpesk.bzh/redpesk-devel/releases/28/images/minimal/x86_64/latest/RedPesk-minimal-28_II-1.x86_64.raw.xz"
                          }

# INTEL RTM request body
RTM_REQ_JSON_BODY_ARM = {
                            "type": "Virtual",
	                        "model": "qemu-system-aarch64",
                            "redpesk_image": "Redpesk-Devel-minimal-28_II.m3ulcb-1.aarch64.raw.xz",
	                        "redpesk_image_link": "https://download.redpesk.bzh/redpesk-devel/releases/28/images/minimal/aarch64/latest/Redpesk-Devel-minimal-28_II.m3ulcb-1.aarch64.raw.xz"
                          }

@sio.event
async def disconnect():
    print("\n")
    print("=======================================================")
    print("==== EVENT: Websocket server ask for disconnection ====")
    print("=======================================================")
    print("Websocket disconnected")


@sio.on('lxc_ready')
async def lxc_ready(data):
    global is_lxc_ready
    print("\n")
    print("-----------------> EVENT: LXC READY <-----------------")
    print(data)
    is_lxc_ready = True


@sio.on('lxc_stopped')
async def lxc_stopped(data):
    print("\n")
    print("----------> EVENT: LXC STOPPED <----------")
    print(data)


@sio.on('rtm_down')
async def rtm_down(data):
    print("\n")
    print("-----------> EVENT: RTM DOWN <-----------")
    print(data)


@sio.on('lxc_deleted')
async def lxc_deleted(data):
    print("\n")
    print("-------------> EVENT: LXC DELETED <------------")
    print(data)


@sio.on('tests_logs_available')
async def logs_available(data):
    print("\n")
    print("-------> EVENT: INTEGRATION TESTS LOGS AVAILABLE <--------")
    print(data)


@sio.on('image_dwnld_failure')
async def image_dwnld_failure(data):
    print("\n")
    print("-------------> EVENT: IMAGE DOWNLOAD FAILURE <------------")
    print(data)


@sio.on('lxc_creation_failure')
async def lxc_creation_failure(data):
    print("\n")
    print("------------> EVENT: LXC CREATION FAILURE <------------")
    print(data)


async def start_server(session):
    print("================================================")
    print("==== Connection to the RTM API Websocket... ====")
    print("================================================")
    print("\n")
    print(str(session.cookie_jar))
    cook = ""
    for cookie in session.cookie_jar:
        cook = cook + cookie.key + "=" + cookie.value + ";" + " "

    print("Cookies to use while asking for connection: " + str(cook))
    headers = {"Cookie": cook}

    print("Waiting for connection to be accepted...")
    await sio.connect(("http://" + SERVER_IP_ADDRESS + ":8080"), headers=headers)
    print("Websocket connection accepted")
    print("\n")


async def fetch(session, url):
    global is_lxc_ready

    print("****************************************************************")
    print("********** Starting the RedTunaMagiC Ship test client **********")
    print("****************************************************************")
    print("\n")

    print("========================================")
    print("==== Get the version of the RTM API ====")
    print("========================================")
    print("\n")

    async with session.get(url+"/version") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")
    await asyncio.sleep(1)

    print("===========================================================")
    print("==== Connect to the Websocket available on the RTM API ====")
    print("===========================================================")
    print("\n")
    await start_server(session)
    await asyncio.sleep(1)

    print("==============================================")
    print("==== Subscribe to the \"LXC Ready\" event ====")
    print("==============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=lxc_ready") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("===============================================")
    print("==== Subscribe to the \"LXC Stopped\" event ===")
    print("===============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=lxc_stopped") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("=============================================")
    print("==== Subscribe to the \"RTM Down\" event ====")
    print("=============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=rtm_down") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("=============================================")
    print("== Subscribe to the \"LXC Deleted\" event ===")
    print("=============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=lxc_deleted") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("=======================================================")
    print("== Subscribe to the \"Image download failure\" event ==")
    print("=======================================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=image_dwnld_failure") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("===================================================")
    print("= Subscribe to the \"LXC creation failure\" event =")
    print("===================================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=lxc_creation_failure") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    something = await aioconsole.ainput('>>> Press enter to request a RTM\n')

    print("=============================================")
    print("====== Ask RTMShip API to launch a RTM ======")
    print("=============================================")
    print("\n")
    async with session.post(url+"/api/v1/rtm/request", json=RTM_REQ_JSON_BODY_INTEL) as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        content = await response.json()
        print(content)
        token_id = content["rtm_token_id"]
        print("-----------------------------")
        print("\n")

    # something = await aioconsole.ainput('>>> Press enter to stop the requested RTM\n')
    # Await for the lxc to be ready to stop it directly
    while (not is_lxc_ready):
        await asyncio.sleep(0.01)

    print("=========================================")
    print("==== Ask RTMShip API to stop the RTM ====")
    print("=========================================")
    print("\n")
    stop_json = {"rtm_token_id": token_id}
    async with session.post(url+"/api/v1/rtm/stop", json=stop_json) as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    await asyncio.sleep(1)

    something = await aioconsole.ainput('>>> Press enter to stop the script\n')


async def main():
    # Creating its cookie jar with unsafe at True allows to automatically
    # manage the cookie even from a server with IP address and not a
    # domain name.
    # Cf. https://aiohttp.readthedocs.io/en/stable/client_advanced.html#cookie-safety
    jar = aiohttp.CookieJar(unsafe=True)
    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        await fetch(session, ("http://" + SERVER_IP_ADDRESS + ":8080"))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
