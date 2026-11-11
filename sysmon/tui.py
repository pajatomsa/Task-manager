"""
Jednoduché a přehledné TUI rozhraní pro terminálový monitor systému (Textual).
Implementace základního uživatelského rozhraní k milníku 11. 11. 2026.
"""

from typing import Optional
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from sysmon.system_service import ProcessInfo, SystemService


class KillConfirmModal(ModalScreen[bool]):
    """Potvrzovací dialog pro ukončení vybraného procesu."""

    DEFAULT_CSS = """
    KillConfirmModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.6);
    }
    #dialog {
        width: 55;
        height: auto;
        border: thick red;
        background: $surface;
        padding: 1 2;
    }
    #dialog-buttons {
        width: 100%;
        align: center middle;
        margin-top: 1;
    }
    #dialog-buttons Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Zrušit"),
        Binding("enter", "confirm", "Potvrdit"),
    ]

    def __init__(self, process: ProcessInfo) -> None:
        super().__init__()
        self.process = process

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(
                f"[bold red]Ukončit proces?[/]\n\n"
                f"Opravdu chcete ukončit proces [bold cyan]{self.process.name}[/] "
                f"(PID: [yellow]{self.process.pid}[/])?",
            )
            with Horizontal(id="dialog-buttons"):
                yield Button("Ukončit (Kill)", variant="error", id="btn-confirm")
                yield Button("Zrušit", id="btn-cancel")

    @on(Button.Pressed, "#btn-confirm")
    def on_confirm(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel(self) -> None:
        self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class SystemMonitorApp(App):
    """Hlavní aplikace terminálového správce úloh."""

    TITLE = "Terminálový správce procesů"

    CSS = """
    #stats {
        height: 3;
        margin: 0 1;
        background: $surface;
        padding: 0 1;
        content-align: left middle;
    }
    #search-box {
        height: 3;
        margin: 0 1;
    }
    #search-input {
        width: 100%;
    }
    DataTable {
        height: 1fr;
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Konec"),
        Binding("/", "focus_search", "Hledat (/)"),
        Binding("k", "kill_selected", "Ukončit (k)"),
        Binding("c", "sort_by_cpu", "Řadit CPU"),
        Binding("m", "sort_by_mem", "Řadit RAM"),
        Binding("p", "sort_by_pid", "Řadit PID"),
        Binding("n", "sort_by_name", "Řadit Název", show=False),
        Binding("r", "manual_refresh", "Obnovit (r)"),
    ]

    def __init__(self, system_service: Optional[SystemService] = None) -> None:
        super().__init__()
        self.service = system_service or SystemService()
        self.sort_by = "cpu_percent"
        self.sort_reverse = True
        self.filter_text = ""
        self.current_processes: list[ProcessInfo] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("Načítání metrik...", id="stats")
        with Horizontal(id="search-box"):
            yield Input(
                placeholder="Hledat proces (/ pro hledání, ESC pro návrat do tabulky)...",
                id="search-input",
            )
        yield DataTable(id="process-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#process-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("PID", "Název", "Uživatel", "CPU %", "RAM %", "RAM (MB)", "Stav")

        self.refresh_data()
        self.set_interval(2.0, self.refresh_data)

    def refresh_data(self) -> None:
        """Obnoví statistiky CPU/RAM a tabulku procesů."""
        if not self.is_running:
            return

        # 1. Horní informační lišta
        metrics = self.service.get_hardware_metrics()
        sort_names = {"cpu_percent": "CPU", "memory_percent": "RAM", "pid": "PID", "name": "Název"}
        sort_label = sort_names.get(self.sort_by, self.sort_by.upper())
        order_symbol = "↓" if self.sort_reverse else "↑"

        stats_text = (
            f" [bold cyan]CPU:[/] {metrics.cpu_percent:4.1f}%  |  "
            f"[bold magenta]RAM:[/] {metrics.ram_percent:4.1f}% ({metrics.ram_used_gb:.1f}/{metrics.ram_total_gb:.1f} GB)  |  "
            f"[bold yellow]Procesů:[/] {metrics.total_processes}  |  "
            f"Řazení: [green]{sort_label} {order_symbol}[/]"
        )
        try:
            self.query_one("#stats", Label).update(stats_text)
        except Exception:
            pass

        # 2. Načtení procesů a naplnění tabulky
        table = self.query_one("#process-table", DataTable)
        current_row = table.cursor_row
        self.current_processes = self.service.get_processes(
            sort_by=self.sort_by,
            reverse=self.sort_reverse,
            filter_text=self.filter_text,
        )

        table.clear()
        for p in self.current_processes:
            table.add_row(
                str(p.pid),
                p.name,
                p.username,
                f"{p.cpu_percent:4.1f}%",
                f"{p.memory_percent:4.1f}%",
                f"{p.memory_mb:6.1f} MB",
                p.status,
                key=str(p.pid),
            )

        if self.current_processes:
            target_row = min(current_row, len(self.current_processes) - 1) if current_row >= 0 else 0
            table.move_cursor(row=target_row)

    @on(Input.Changed, "#search-input")
    def on_search_changed(self, event: Input.Changed) -> None:
        self.filter_text = event.value
        self.refresh_data()

    @on(Input.Submitted, "#search-input")
    def on_search_submitted(self) -> None:
        self.query_one("#process-table", DataTable).focus()

    def get_selected_process(self) -> Optional[ProcessInfo]:
        table = self.query_one("#process-table", DataTable)
        if not self.current_processes:
            return None
        row = table.cursor_row
        if 0 <= row < len(self.current_processes):
            return self.current_processes[row]
        return None

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    def action_kill_selected(self) -> None:
        proc = self.get_selected_process()
        if not proc:
            self.notify("Není vybrán žádný proces.", severity="warning")
            return

        def on_confirm(confirmed: bool) -> None:
            if confirmed:
                ok, msg = self.service.terminate_process(proc.pid)
                self.notify(msg, severity="information" if ok else "error")
                self.refresh_data()

        self.push_screen(KillConfirmModal(proc), on_confirm)

    def _toggle_or_set_sort(self, key: str) -> None:
        if self.sort_by == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_by = key
            self.sort_reverse = False if key == "name" else True
        self.refresh_data()

    def action_sort_by_cpu(self) -> None:
        self._toggle_or_set_sort("cpu_percent")

    def action_sort_by_mem(self) -> None:
        self._toggle_or_set_sort("memory_percent")

    def action_sort_by_pid(self) -> None:
        self._toggle_or_set_sort("pid")

    def action_sort_by_name(self) -> None:
        self._toggle_or_set_sort("name")

    def action_manual_refresh(self) -> None:
        self.refresh_data()
        self.notify("Data obnovena", timeout=1.0)
