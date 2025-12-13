"""State for financial statement display and management."""

import reflex as rx
import io
import csv


class FinancialStatementState(rx.State):
    """State for managing financial statement dialogs and exports."""

    expanded_table: int = -1

    @rx.event
    def expand(self, idx: int):
        """Expand a financial statement table in dialog."""
        self.expanded_table = idx

    @rx.event
    def handle_dialog_open(self, value: bool):
        """Handle dialog open/close state."""
        if not value:
            self.expanded_table = -1

    @rx.event
    def close(self):
        """Close the expanded table dialog."""
        self.expanded_table = -1

    @rx.event
    def download_table_csv(self, data: list, idx: int):
        """Download financial statement as CSV."""
        titles = ["Income_Statement", "Balance_Sheet", "Cash_Flow"]
        ticker = self.ticker
        if not data:
            return
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        csv_data = output.getvalue()
        output.close()
        return rx.download(data=csv_data, filename=f"{ticker}_{titles[idx]}.csv")
