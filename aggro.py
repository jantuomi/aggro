import json
import os

from app.AggroConfig import AggroConfig
from app.PluginManager import PluginManager

if __name__ == "__main__":
    print("Starting aggro. Press CTRL-C to exit.")

    aggrofile_path = os.environ.get("AGGRO_CONFIG_PATH", "Aggrofile")

    with open(aggrofile_path) as f:
        aggrofile_content = json.loads(f.read())

    aggro_config = AggroConfig(
        plugins=aggrofile_content["plugins"], graph=aggrofile_content["graph"]
    )

    manager = PluginManager(aggro_config)
    manager.build_plugin_instances()

    try:
        manager.run()
    except KeyboardInterrupt:
        print("Exiting...")
