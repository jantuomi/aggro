import importlib
import schedule
import time
from types import ModuleType
from typing import Any
from app.Item import Item
from app.PluginInterface import Params, PluginInterface
from app.AggroConfig import AggroConfig
from app.utils import get_param
from app.MemoryState import memory_state


class PluginManager:
    def __init__(self, config: AggroConfig) -> None:
        self._plugins: dict[str, Any] = {}
        self.plugin_instances: dict[str, PluginInterface] = {}
        self.config = config

    def load_plugin(self, plugin_name: str) -> None:
        module: ModuleType = importlib.import_module(f"plugins.{plugin_name}")
        plugin_class = module.Plugin
        self._plugins[plugin_name] = plugin_class

    def propagate(self, id: str, items: list[Item]):
        next_nodes: list[str]
        if id not in self.config.graph:
            next_nodes = []
        else:
            next_nodes = self.config.graph[id]

        for next_node_id in next_nodes:
            self.run_plugin_job(next_node_id, id, items)

    def run_plugin_job(self, id: str, source_id: str | None, items: list[Item] = []):
        if not memory_state.running:
            return

        plugin: PluginInterface = self.plugin_instances[id]
        ret_items: list[Item] = plugin.process(source_id, items)
        self.propagate(id, ret_items)

    def build_plugin_instances(self):
        self.graph: dict[str, PluginInterface] = {}
        for id in self.config.plugins:
            params: Params = self.config.plugins[id]

            plugin_name = get_param("plugin", params)
            schedule_expr: str | None = params.get("schedule_expr", None)

            if plugin_name not in self._plugins:
                self.load_plugin(plugin_name)

            if schedule_expr is not None:
                job: schedule.Job = eval(schedule_expr, {"schedule": schedule})
                job.do(self.run_plugin_job, id, None)  # type: ignore

            PluginClass: Any = self._plugins[plugin_name]
            plugin: PluginInterface = PluginClass(id=id, params=params)
            self.plugin_instances[id] = plugin

    def run(self) -> None:
        while memory_state.running:
            schedule.run_pending()
            time.sleep(1)
