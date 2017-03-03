from shakedown import *

DCOS_URL = shakedown.run_dcos_command('config show core.dcos_url')[0].strip()
PACKAGE_NAME = "neo4j"
SERVICE_NAME = "core-neo4j"
TASK_RUNNING_STATE = 'TASK_RUNNING'
DEFAULT_CLUSTER_SIZE = 3
WAIT_TIME_IN_SECONDS = 60

def test_install_neo4j():
    uninstall()
    install_package_and_wait(PACKAGE_NAME, wait_for_completion=True, service_name=SERVICE_NAME)
    assert package_installed(PACKAGE_NAME, service_name=SERVICE_NAME), 'Package failed to install'

    check_health()

    uninstall()

def uninstall():
    try:
        uninstall_package_and_wait(PACKAGE_NAME, service_name=SERVICE_NAME)
    except (dcos.errors.DCOSException, ValueError) as e:
        print('Got exception when uninstalling package, continuing with janitor anyway: {}'.format(e))

def check_health():
    def fn():
        try:
            return shakedown.get_service_tasks(SERVICE_NAME)
        except dcos.errors.DCOSHTTPException:
            return []

    def success_predicate(tasks):
        running_tasks = [t for t in tasks if t['state'] == TASK_RUNNING_STATE]
        print('Waiting for {} healthy tasks, got {}/{}'.format(
            DEFAULT_CLUSTER_SIZE, len(running_tasks), len(tasks)))
        return (
            len(running_tasks) == DEFAULT_CLUSTER_SIZE,
            'Service did not become healthy'
        )

    return spin(fn, success_predicate)

def spin(fn, success_predicate, *args, **kwargs):
    now = time.time()
    end_time = now + WAIT_TIME_IN_SECONDS
    while now < end_time:
        print("%s: %.01fs left" % (time.strftime("%H:%M:%S %Z", time.localtime(now)), end_time - now))
        result = fn(*args, **kwargs)
        is_successful, error_message = success_predicate(result)
        if is_successful:
            print('Success state reached, exiting spin.')
            break
        print('Waiting for success state... err={}'.format(error_message))
        time.sleep(1)
        now = time.time()

    assert is_successful, error_message

    return result
