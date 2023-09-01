import importlib
import schedule
import time
from types import ModuleType
from typing import Any
from app.Item import Item
from app.PluginInterface import PluginInterface
from app.AggroConfig import AggroConfig
from app.utils import get_param


class PluginManager:
    def __init__(self, config: AggroConfig) -> None:
        self._plugins: dict[str, Any] = {}
        self.plugin_instances: dict[str, PluginInterface] = {}
        self.running = False
        self.config = config

    def load_plugin(self, plugin_name: str) -> None:
        module: ModuleType = importlib.import_module(f"app.{plugin_name}")
        plugin_class = module.Plugin
        self._plugins[plugin_name] = plugin_class

    def propagate(self, id: str, items: list[Item]):
        next_nodes: list[str]
        if id not in self.config.graph:
            next_nodes = []
        else:
            next_nodes = self.config.graph[id]

        for next_node_id in next_nodes:
            self.run_plugin_job(next_node_id, items)

    def run_plugin_job(self, id: str, items: list[Item] = []):
        if not self.running:
            return

        plugin: PluginInterface = self.plugin_instances[id]
        ret_items: list[Item] = plugin.process([items])
        self.propagate(id, ret_items)

    def build_plugin_instances(self):
        self.graph: dict[str, PluginInterface] = {}
        for id in self.config.plugins:
            params: dict[str, str] = self.config.plugins[id]

            plugin_name = get_param("plugin", params)
            trigger_type = get_param("trigger_type", params)

            if plugin_name not in self._plugins:
                self.load_plugin(plugin_name)

            match trigger_type:
                case "schedule":
                    schedule_expr = get_param("schedule_expr", params)
                    job: schedule.Job = eval(schedule_expr, {"schedule": schedule})
                    job.do(self.run_plugin_job, id)  # type: ignore
                case "input_change":
                    pass
                case _:
                    raise Exception("unknown trigger_type: " + trigger_type)

            PluginClass: Any = self._plugins[plugin_name]
            plugin: PluginInterface = PluginClass(id=id, params=params)
            self.plugin_instances[id] = plugin

    def run(self) -> None:
        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(1)
