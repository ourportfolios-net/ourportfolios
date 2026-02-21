import re


def preprocess_events_to_text(events: list) -> list:
    """Convert list of event dicts to list of formatted text strings for individual parsing"""
    text_blocks = []

    for event in events:
        event_desc = event.get("event_desc", "")
        notify_date = event.get("notify_date", "")
        exec_date = event.get("exer_date", "")

        # Skip financial statements and irrelevant events
        if "Financial Statement" in event_desc:
            continue

        # Only process transaction events
        if "Name of person/ corporation that conducts the transfer:" not in event_desc:
            continue

        # Append the dates to the event description
        enhanced_desc = f"{event_desc} Notify: {notify_date}, Exec: {exec_date}"
        text_blocks.append(enhanced_desc)

    return text_blocks


def preprocess_events_texts(text: str) -> str:
    summaries = []
    lines = text.strip().splitlines()

    buffer = ""
    for line in lines:
        if re.match(
            r"^\s*- Name of person/ corporation that conducts the transfer:", line
        ):
            if buffer:
                summaries.append(buffer.strip())
                buffer = ""
        buffer += " " + line.strip()
    if buffer:
        summaries.append(buffer.strip())

    final_outputs = []

    for entry in summaries:
        if "Financial Statement" in entry:
            continue

        def get(pattern):
            match = re.search(pattern, entry)
            return match.group(1).strip() if match else ""

        name = get(r"transfer:\s*(.*?)\s*-")
        position = get(r"Current position:\s*(.*?)\s*-")
        tx_type = get(r"Type of transaction registered:\s*(.*?)\s*-")

        # Extract shares and percentages
        shares_before = get(r"before the transaction:\s*([\d,]+)\s*shares").replace(
            ",", ""
        )
        percent_before = get(r"before the transaction:.*?([\d.]+%)")
        shares_registered = get(
            r"Number of shares registered:\s*([\d,]+)\s*shares"
        ).replace(",", "")
        acquired_shares = get(r"Acquired shares:\s*([-\d,]+)\s*shares").replace(",", "")
        shares_after = get(r"after the transaction:\s*([\d,]+)\s*shares").replace(
            ",", ""
        )
        percent_after = get(r"after the transaction:.*?([\d.]+%)")
        exec_date = get(r"Exec:\s*(\d{4}-\d{2}-\d{2})")

        # Calculate percentage difference and registered shares percentage
        try:
            before_pct = float(percent_before.replace("%", ""))
            after_pct = float(percent_after.replace("%", ""))
            pct_diff = after_pct - before_pct
            pct_diff_str = f" ({pct_diff:+.2f}% change)"
        except Exception:
            pct_diff_str = ""

        # Calculate percentage of registered shares relative to initial holdings
        try:
            registered_pct = (float(shares_registered) / float(shares_before)) * 100
            registered_pct_str = f" ({registered_pct:.2f}% of initial)"
        except Exception:
            registered_pct_str = ""

        summary = (
            f"{name} ({position}) executed {tx_type.upper()} {shares_registered} shares{registered_pct_str} on {exec_date} "
            f"from {shares_before} shares ({percent_before}) to {shares_after} shares ({percent_after}). "
            f"Acquired: {acquired_shares} shares{pct_diff_str}."
        )

        final_outputs.append(summary)

    return "\n".join(final_outputs)


def process_events_for_display(events: list) -> list:
    """
    Process events and return them in the format expected by your lambda function.
    Preprocesses only transaction events' descriptions and retains all other fields.
    """
    processed_events = []

    for event in events:
        event_desc = event.get("event_desc", "")

        # Process only if it's a transaction event
        if "Name of person/ corporation that conducts the transfer:" in event_desc:
            # Enhance with dates
            enhanced_desc = f"{event_desc} Notify: {event.get('notify_date', '')}, Exec: {event.get('exer_date', '')}"
            # Preprocess this single event
            summary_text = preprocess_events_texts(enhanced_desc)
            summary_lines = [
                line.strip() for line in summary_text.split("\n") if line.strip()
            ]
            summary = summary_lines[0] if summary_lines else event_desc

            # Extract exec date if found
            exec_date_match = re.search(r"on (\d{4}-\d{2}-\d{2})", summary)
            exec_date = (
                exec_date_match.group(1)
                if exec_date_match
                else event.get("exer_date", "")
            )

            new_event = event.copy()
            new_event["event_desc"] = summary
            new_event["exer_date"] = exec_date
            new_event["notify_date"] = ""  # Optional: keep "" or original
            processed_events.append(new_event)
        else:
            processed_events.append(event.copy())

    return processed_events
