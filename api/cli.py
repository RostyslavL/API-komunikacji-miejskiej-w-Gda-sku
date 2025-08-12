import time
import json
import argparse
from tabulate import tabulate
from app.services import ztm
from app import db

DEFAULT_CONFIG = "config/stops.json"

def load_config(path=DEFAULT_CONFIG):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pretty_table(rows):
    table = []
    for r in rows:
        delay = r["delay_seconds"]
        delay_str = f"{delay}s" if delay else ""
        table.append([r["line"], r["direction"], r["time_local"] or "", r["status"], delay_str])
    return tabulate(table, headers=["Line", "Direction", "Time", "Status", "Delay"], tablefmt="grid")

def run(interval=20, combined=False, config_path=DEFAULT_CONFIG):
    cfg = load_config(config_path)
    api_base = cfg.get("api_base")
    stop01 = cfg.get("01")
    stop02 = cfg.get("02")
    try:
        while True:
            all_rows = []
            if stop01:
                deps1 = ztm.get_departures_api(api_base, stop01)
                print("=== Brama Wyżynna 01 ===")
                print(pretty_table(deps1))
                all_rows.extend(deps1)
            if stop02:
                deps2 = ztm.get_departures_api(api_base, stop02)
                print("=== Brama Wyżynna 02 ===")
                print(pretty_table(deps2))
                all_rows.extend(deps2)
            if all_rows:
                db.save_departures_history(all_rows)
            print(f"\n(odświeżenie za {interval}s) — Ctrl+C aby wyjść")
            time.sleep(interval)
            print("\033[H\033[J", end="")  # clear
    except KeyboardInterrupt:
        print("Zakończono.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--interval", type=int, default=20)
    parser.add_argument("--combined", action="store_true")
    args = parser.parse_args()
    run(args.interval, args.combined, args.config)
