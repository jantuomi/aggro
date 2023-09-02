import json
import os

# from multiprocessing import Process
from threading import Thread
import time
from app.AggroConfig import AggroConfig
from app.MemoryState import memory_state
from app.PluginManager import PluginManager
from app.database import database_manager
from app.server import run_web_server


def run_plugin_thread(manager: PluginManager, config: AggroConfig):
    print("Plugin thread starting...")
    manager.run()
    print("Plugin thread exiting...")


def run_server_thread(config: AggroConfig):
    print("Server thread starting...")
    run_web_server(config.server_host, config.server_port)
    print("Server thread exiting...")


if __name__ == "__main__":
    print("Starting aggro. Press CTRL-C to exit.")

    aggrofile_path = os.environ.get("AGGRO_CONFIG_PATH", "Aggrofile")

    with open(aggrofile_path) as f:
        aggrofile_content = json.loads(f.read())

    aggro_config = AggroConfig(
        server_host=aggrofile_content.get("server_host", "localhost"),
        server_port=aggrofile_content.get("server_port", 8080),
        db_path=aggrofile_content.get("db_path", "db.json"),
        plugins=aggrofile_content["plugins"],
        graph=aggrofile_content["graph"],
    )

    database_manager.setup(aggro_config)

    manager = PluginManager(aggro_config)
    manager.build_plugin_instances()

    memory_state.running = True

    plugin_thread = Thread(target=run_plugin_thread, args=[manager, aggro_config])
    plugin_thread.start()

    server_thread = Thread(target=run_server_thread, args=[aggro_config])
    server_thread.daemon = True
    server_thread.start()

    try:
        while memory_state.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        memory_state.running = False
        print("Waiting for threads to exit...")
        plugin_thread.join()
        print("Server thread exiting...")
        print("Main thread exiting...")
