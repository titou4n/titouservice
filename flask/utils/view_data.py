import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from Data.database_handler import DatabaseHandler
from utils.utils import Utils

class ViewDataWithMatplolib():
    def __init__(self, utils:Utils, database_handler:DatabaseHandler):
        self.utils = utils
        self.database_handler=database_handler
        self.color = "#9B7ED8"
        self.path = "connections_per_day.png"

    def get_graph_connection_per_day_by_user(self, id: int, output_path:str) -> None:
        data = self.database_handler.get_metadata(id)

        if not data:
            raise ValueError(f"No metadata found for id {id}")

        connections_per_day: dict[str, int] = {}
        for record in data:
            date = self.utils.format_date(record["date_connected"])
            connections_per_day[date] = connections_per_day.get(date, 0) + 1

        self.get_graph_bar_connection_per_day(connections_per_day=connections_per_day, output_path=output_path)

    def get_graph_connection_per_day(self, output_path:str, type_graph:str = "bar") -> None:
        data = self.database_handler.get_all_metadata()

        if not data:
            raise ValueError(f"No metadata found")

        connections_per_day: dict[str, int] = {}
        for record in data:
            date = self.utils.format_date(record["date_connected"])
            connections_per_day[date] = connections_per_day.get(date, 0) + 1

        match type_graph:
            case "bar":
                self.get_graph_bar_connection_per_day(connections_per_day, output_path)
            case "stackplot":
                self.get_graph_stackplot_connection_per_day(connections_per_day, output_path)
            case _:
                self.get_graph_bar_connection_per_day(connections_per_day, output_path)

    def get_graph_bar_connection_per_day(self, connections_per_day:dict, output_path:str) -> None:

        if not connections_per_day:
            raise ValueError("connections_per_day is empty.")
        
        dates = list(connections_per_day.keys())
        counts = list(connections_per_day.values())
        x = np.arange(len(counts))

        fig, ax = plt.subplots(figsize=(max(6, len(dates) * 0.6), 5))
        ax.bar(x, counts, width=1, color=self.color, edgecolor="white")

        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha="right")
        ax.set_xlabel("Date")
        ax.set_ylabel("Connections")
        ax.set_title(f"Connections per Day — Graph")
        ax.yaxis.get_major_locator().set_params(integer=True)  # whole numbers only

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

    def get_graph_stackplot_connection_per_day(self, connections_per_day:dict, output_path:str) -> None:

        if not connections_per_day:
            raise ValueError("connections_per_day is empty.")

        dates = list(connections_per_day.keys())
        counts = list(connections_per_day.values())
        x = np.arange(len(dates))

        fig, ax = plt.subplots(figsize=(max(6, len(dates) * 0.6), 5))

        fig.patch.set_alpha(0)   # fond de la figure transparent
        ax.patch.set_alpha(0)    # fond des axes transparent

        ax.stackplot(x, counts, color=self.color, alpha=0.8)

        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha="right")
        ax.set_xlim(0, len(dates)-1)
        ax.set_ylim(0, max(counts) + 1)
        ax.set_xlabel("Date")
        ax.set_ylabel("Connections")
        ax.set_title("Connections per Day — Graph")
        ax.yaxis.get_major_locator().set_params(integer=True)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight", transparent=True)
        plt.close(fig)