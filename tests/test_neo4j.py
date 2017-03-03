import uuid

from shakedown import *
from dcos import *

DCOS_URL = shakedown.run_dcos_command('config show core.dcos_url')[0].strip()
PACKAGE_NAME = "neo4j"
SERVICE_NAME = "core-neo4j"
TASK_RUNNING_STATE = 'TASK_RUNNING'
DEFAULT_CLUSTER_SIZE = 3
WAIT_TIME_IN_SECONDS = 60

def test_install_neo4j():
    # spin up cluster - mesos.py

    # install package,
    # uninstall()
    # install_package_and_wait(PACKAGE_NAME, wait_for_completion=True, service_name=SERVICE_NAME)
    assert package_installed(PACKAGE_NAME, service_name=SERVICE_NAME), 'Package failed to install'

    check_health()

    # do basic queries
    client = marathon.create_client()

    app_id = uuid.uuid4().hex

    app_json = {
     "id": app_id,
     "env": {
       "NEO4J_BOLT_URL": "bolt://neo4j:dcos@core-neo4j.marathon.containerip.dcos.thisdcos.directory:7687",
       "CONCURRENCY": "4",
       "MAX_OPERATIONS": "5000"
     },
     "instances": 1,
     "cpus": 1,
     "mem": 1000,
     "disk": 500,
     "container": {
       "docker": {
         "image": "unterstein/neo4j-twitter-load",
         "forcePullImage": True
       }
     }
    }

    client.add_app(app_json)

    deployment_wait()

    tasks = client.get_tasks(app_id)
    assert len(tasks) == 1

    # scale up one node
    # done.

    # uninstall()

def uninstall():
    try:
        uninstall_package_and_wait(PACKAGE_NAME, service_name=SERVICE_NAME)
    except (dcos.errors.DCOSException, ValueError) as e:
        print('Got exception when uninstalling package, continuing with janitor anyway: {}'.format(e))

def check_health():
    def fn():
        try:
            return shakedown.get_service_tasks("marathon")
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
