import json
import os
import hashlib
from dotenv import load_dotenv
from threading import Thread
import time
from typing import Any

from tinydb import Query
from app.AggroConfig import AggroConfig, AggroConfigServer, AggroConfigEmailAlerter
from app.MemoryState import memory_state
from app.PluginManager import PluginManager
from app.DatabaseManager import database_manager
from app.server import run_web_server
from app.utils import get_config, get_config_or_default

load_dotenv()


def run_plugin_thread(manager: PluginManager, config: AggroConfig):
    print("Plugin thread starting...")
    manager.run()
    print("Plugin thread exiting...")


def run_server_thread(config: AggroConfig):
    print("Server thread starting...")
    run_web_server(config.server.host, config.server.port)
    print("Server thread exiting...")


if __name__ == "__main__":
    print("Starting aggro. Press CTRL-C to exit.")

    aggrofile_path = os.environ.get("AGGRO_CONFIG_PATH", "Aggrofile")

    with open(aggrofile_path) as f:
        aggrofile_content = f.read()
        aggrofile = json.loads(aggrofile_content)

    aggrofile_server = get_config_or_default(aggrofile, "server", {})
    server_config = AggroConfigServer(
        host=get_config_or_default(aggrofile_server, "host", "localhost"),
        port=get_config_or_default(aggrofile_server, "port", 8080),
    )

    aggrofile_email_alerter = get_config_or_default(aggrofile, "email_alerter", None)
    if aggrofile_email_alerter:
        email_alerter_config = AggroConfigEmailAlerter(
            api_url=get_config(aggrofile_email_alerter, "api_url"),
            api_auth=get_config(aggrofile_email_alerter, "api_auth"),
            email_from=get_config(aggrofile_email_alerter, "email_from"),
            email_to=get_config(aggrofile_email_alerter, "email_to"),
        )
    else:
        email_alerter_config = None

    aggro_config = AggroConfig(
        server=server_config,
        email_alerter=email_alerter_config,
        db_path=get_config_or_default(aggrofile, "db_path", "db.json"),
        plugins=get_config(aggrofile, "plugins"),
        graph=get_config(aggrofile, "graph"),
    )

    database_manager.setup(aggro_config)

    aggrofile_hash_q = Query().key == "aggrofile_hash"
    aggrofile_stored_hash: str | None
    if database_manager.meta_info.contains(aggrofile_hash_q):
        aggrofile_stored_hash_obj: Any = database_manager.meta_info.get(
            aggrofile_hash_q
        )
        aggrofile_stored_hash = aggrofile_stored_hash_obj["value"]
    else:
        aggrofile_stored_hash = None

    aggrofile_current_hash = hashlib.sha256(aggrofile_content.encode("utf-8"))
    aggrofile_current_hash_dig = aggrofile_current_hash.hexdigest()

    if (
        aggrofile_stored_hash is not None
        and aggrofile_stored_hash != aggrofile_current_hash_dig
    ):
        # Aggrofile has been changed
        print("Aggrofile has been changed. Truncating plugin states in DB...")
        database_manager.plugin_states.truncate()

    database_manager.meta_info.upsert(
        {"key": "aggrofile_hash", "value": aggrofile_current_hash_dig},
        aggrofile_hash_q,
    )

    manager = PluginManager(aggro_config)
    manager.build_plugin_instances()

    memory_state.running = True

    server_thread = Thread(target=run_server_thread, args=[aggro_config])
    server_thread.daemon = True
    server_thread.start()

    manager.initial_run_scheduled_plugins()

    plugin_thread = Thread(target=run_plugin_thread, args=[manager, aggro_config])
    plugin_thread.start()

    try:
        while memory_state.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        memory_state.running = False
        print("Waiting for threads to exit...")
        plugin_thread.join()
        print("Server thread exiting...")
        print("Main thread exiting...")
