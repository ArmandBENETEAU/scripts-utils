import aiohttp
import asyncio
import aioconsole
import time
import socketio

sio = socketio.AsyncClient()
start_timer = None

SERVER_IP_ADDRESS = "localhost"


# RTM request body
PW_ON_JSON_BODY_INTEL = {
                            "target_model": "x86-64",
                            "image_details":
                            {
                                "image_path": "/home/armand/work_local/tmp_development/red-tuna-magic/red_tuna_magic_test/tmp_download/RedPesk-minimal-28_II-1.x86_64.raw",
                                "login": "root",
                                "password": "root"
                            },
                            "launching_options":
                            {
                                "waitboot": False,
                                "can_init": False,
                                "read_only": True
                            }
                        }

PW_ON_JSON_BODY_ARM = {
                        "target_model": "aarch64",
                        "image_details":
                        {
                            "image_path": "/home/armand/work_local/tmp_development/red-tuna-magic/red_tuna_magic_test/tmp_download/Redpesk-Devel-minimal-28_II.m3ulcb-1.aarch64.raw",
                            "kernel_path": "/home/armand/work_local/tmp_development/red-tuna-magic/red_tuna_magic_test/tmp_download/Image",
                            "login": "root",
                            "password": "root"
                        },
                        "launching_options":
                        {
                            "waitboot": False,
                            "can_init": False,
                            "read_only": True
                        }
                      }

TEST_START_JSON_BODY = {
                        "test_type": "RED_TESTS_TYPE",
                        "pkg": "agl-service-helloworld",
                        "pkg_repository": "http://community-hub-prod01.redpesk.iot/kojifiles/repos/seb-prj-2505--redpesk-devel-28-build/latest/x86_64",
                        "test_time_out": 3000
                       }

@sio.event
async def disconnect():
    print("\n")
    print("=======================================================")
    print("==== EVENT: Websocket server ask for disconnection ====")
    print("=======================================================")
    print("Websocket disconnected")


@sio.on('pw_on')
async def power_on(data):
    print("\n")
    print("-----------------> EVENT: POWER ON DONE <-----------------")


@sio.on('vcan_initialized')
async def vcan_init(data):
    print("\n")
    print("----------> EVENT: VCAN INITIALIZATION IS DONE <----------")


@sio.on('tests_started')
async def start_of_tests(data):
    print("\n")
    print("-----------> EVENT: INTEGRATION TESTS STARTED <-----------")


@sio.on('tests_ended')
async def end_of_tests(data):
    print("\n")
    print("-------------> EVENT: INTEGRATION TESTS DONE <------------")


@sio.on('tests_logs_available')
async def logs_available(data):
    print("\n")
    print("-------> EVENT: INTEGRATION TESTS LOGS AVAILABLE <--------")
    print(data)


@sio.on('tests_result_available')
async def results_available(data):
    print("\n")
    print("-------------> EVENT: TESTS RESULT AVAILABLE <------------")
    print(data)


@sio.on('tests_aborted')
async def tests_aborted(data):
    print("\n")
    print("------------> EVENT: TESTS CORRECTLY ABORTED <------------")

@sio.on('tests_stdout_line')
async def stdout_available(data):
    print("\n")
    print("-------------> EVENT: TESTS STDOUT AVAILABLE <------------")
    print(data)

@sio.on('tests_stderr_line')
async def stderr_available(data):
    print("\n")
    print("-------------> EVENT: TESTS STDERR AVAILABLE <------------")
    print(data)

@sio.on('tests_timed_out')
async def tests_timedout(data):
    print("\n")
    print("-------------> EVENT: TESTS TIMED OUT <------------")

@sio.on('test_progress')
async def stderr_available(data):
    print("\n")
    print("-------------> EVENT: TESTS PROGRESS <------------")
    print(data)

@sio.on('heartbeat')
async def heartbeat(data):
    print("\n")
    print("------------> EVENT: HEARTBEAT <------------")


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
    print("*************************************************************")
    print("********** Starting the Red Tuna MagiC test client **********")
    print("*************************************************************")
    print("\n")
    await asyncio.sleep(2)

    print("========================================")
    print("==== Get the version of the RTM API ====")
    print("========================================")
    print("\n")

    async with session.get(url+"/version") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
#        print("2+++ "+str(response.cookies.get('redtuna_id')))
        print("-----------------------------")
        print("\n")
    await asyncio.sleep(2)

    print("===========================================================")
    print("==== Connect to the Websocket available on the RTM API ====")
    print("===========================================================")
    print("\n")
    await start_server(session)
    await asyncio.sleep(2)

    print("=============================================")
    print("==== Subscribe to the \"Power On\" event ====")
    print("=============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=pw_on") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("=============================================")
    print("==== Subscribe to the \"VCAN init\" event ===")
    print("=============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=vcan_initialized") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("=============================================")
    print("= Subscribe to the \"Start of tests\" event =")
    print("=============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=tests_started") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("=============================================")
    print("== Subscribe to the \"End of tests\" event ==")
    print("=============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=tests_ended") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("===============================================")
    print("== Subscribe to the \"logs available\" event ==")
    print("===============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=tests_logs_available") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("===============================================")
    print("= Subscribe to the \"result available\" event =")
    print("===============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=tests_result_available") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("===============================================")
    print("=== Subscribe to the \"test aborted\" event ===")
    print("===============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=tests_aborted") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("===============================================")
    print("=== Subscribe to the \"heartbeat\" event ===")
    print("===============================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=heartbeat") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("====================================================")
    print("=== Subscribe to the \"tests_stdout_line\" event ===")
    print("====================================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=tests_stdout_line") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("====================================================")
    print("=== Subscribe to the \"tests_stderr_line\" event ===")
    print("====================================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=tests_stderr_line") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("====================================================")
    print("=== Subscribe to the \"tests_timed_out\" event ===")
    print("====================================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=tests_timed_out") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    print("====================================================")
    print("=== Subscribe to the \"test_progress\" event ===")
    print("====================================================")
    print("\n")

    async with session.post(url+"/api/v1/event/subscribe?ev=test_progress") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    something = await aioconsole.ainput('>>> Press enter to ask to start the target\n')

    print("=========================================================")
    print("==== Ask the RTM API to start the target (Qemu here) ====")
    print("=========================================================")
    print("\n")
    async with session.post(url+"/api/v1/target/power/on", json=PW_ON_JSON_BODY_INTEL) as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        content = await response.json()
        print(content)
        print("-----------------------------")
        print("\n")

    # something = await aioconsole.ainput('>>> Press enter to launch integrations tests\n')

    # print("=========================================================")
    # print("====== Ask the RTM to launch the integration tests ======")
    # print("=========================================================")
    # print("\n")

    # async with session.post(url+"/api/v1/target/tests/start", json=TEST_START_JSON_BODY) as response:
    #     print("-----------------------------")
    #     print("---- Answer from RTM API ----")
    #     print(response)
    #     content = await response.text()
    #     print(content)
    #     print("-----------------------------")
    #     print("\n")

    something = await aioconsole.ainput('>>> Press enter to ask RTM API to turn off the Qemu\n')

    print("==============================================")
    print("==== Ask the RTM API to turn Off the Qemu ====")
    print("==============================================")
    print("\n")
    async with session.post(url+"/api/v1/target/power/off") as response:
        print("-----------------------------")
        print("---- Answer from RTM API ----")
        print(response)
        print("-----------------------------")
        print("\n")

    await asyncio.sleep(1)


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
