import json
import os
import threading
import time
from app.AggroConfig import AggroConfig
from app.MemoryState import memory_state
from app.PluginManager import PluginManager
from app.database import setup_db


def run_plugin_thread():
    print("Plugin thread starting...")
    manager.run()
    print("Plugin thread exiting...")


if __name__ == "__main__":
    print("Starting aggro. Press CTRL-C to exit.")

    aggrofile_path = os.environ.get("AGGRO_CONFIG_PATH", "Aggrofile")

    with open(aggrofile_path) as f:
        aggrofile_content = json.loads(f.read())

    aggro_config = AggroConfig(
        db_path=aggrofile_content.get("db_path", "db.json"),
        plugins=aggrofile_content["plugins"],
        graph=aggrofile_content["graph"],
    )

    setup_db(aggro_config)

    manager = PluginManager(aggro_config)
    manager.build_plugin_instances()

    memory_state.running = True

    plugin_thread = threading.Thread(target=run_plugin_thread)
    plugin_thread.start()

    try:
        while memory_state.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        memory_state.running = False
        print("Waiting for threads to exit...")
        plugin_thread.join()
        print("Main thread exiting...")
