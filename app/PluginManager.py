import importlib
import schedule
import time
import sys
import traceback
from types import ModuleType
from typing import Any
from app.Item import Item
from app.PluginInterface import Params, PluginInterface
from app.AggroConfig import AggroConfig, AggroConfigEmailAlerter
from app.utils import get_config
from app.MemoryState import memory_state
from app.EmailAlerter import EmailAlerter


class PluginManager:
    def __init__(self, config: AggroConfig) -> None:
        self._plugins: dict[str, Any] = {}
        self.plugin_instances: dict[str, PluginInterface] = {}
        self.config = config
        self.scheduled_plugin_ids: list[str] = []
        if self.config.email_alerter:
            self.email_alerter = EmailAlerter.from_config(self.config.email_alerter)

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

        try:
            try:
                plugin: PluginInterface = self.plugin_instances[id]
                ret_items: list[Item] = plugin.process(source_id, items)
                self.propagate(id, ret_items)
            except Exception as ex:
                ex.add_note(f"context: plugin id: {id}, source id: {source_id}")
                raise

        except:
            exc = traceback.format_exc()
            print(exc, file=sys.stderr)
            if self.email_alerter:
                self.email_alerter.send_alert(exc)

    def build_plugin_instances(self):
        for id in self.config.plugins:
            params: Params = self.config.plugins[id]

            plugin_name: str = get_config(params, "plugin")
            schedule_expr: str | None = params.get("schedule_expr", None)

            if plugin_name not in self._plugins:
                self.load_plugin(plugin_name)

            if schedule_expr is not None:
                job: schedule.Job = eval(schedule_expr, {"schedule": schedule})
                job.do(self.run_plugin_job, id, None)
                self.scheduled_plugin_ids.append(id)

            PluginClass: Any = self._plugins[plugin_name]
            plugin: PluginInterface = PluginClass(id=id, params=params)
            self.plugin_instances[id] = plugin

    def initial_run_scheduled_plugins(self):
        for id in self.scheduled_plugin_ids:
            self.run_plugin_job(id, None)

    def run(self) -> None:
        while memory_state.running:
            schedule.run_pending()
            time.sleep(1)
