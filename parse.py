#!/usr/bin/env python

import os
import csv
import re

def main(in_fname, consuption_fname, metering_fname) -> int:
    line_re = re.compile(
        r"([0-9][0-9]\.[0-9][0-9]\.[0-9][0-9][0-9][0-9]) "
        r"Расход общедомовых ресурсов \(услуга: расход / инд. /ОДН\): (.*)\. "
        r"Показания ОДПУ \(Услуга \[№ прибора\] - показание\): (.*)\."
    )
    consumption_re = re.compile(
        r" *(.*): (.*) / (.*) / (.*)"
    )
    meter_re = re.compile(
        r" *(.*) - ([0-9.]+)"
    )

    consumption_fields = set()
    metering_fields = set()

    consumption_data = []
    metering_data = []

    with open(in_fname, mode="r", encoding="utf-8") as f:
        for line in f.readlines():
            m = line_re.match(line)
            if not m:
                print(f"Failed to parse line: {line}")
                return 1

            month_consumption = {"date": m.group(1)}
            for consumption in m.group(2).split(";"):
                consumption_m = consumption_re.match(consumption)
                if not consumption_m:
                    print(f"Failed to parse consumption: {consumption}")
                consumption_fields.add(f"{consumption_m.group(1)} расход")
                consumption_fields.add(f"{consumption_m.group(1)} инд")
                consumption_fields.add(f"{consumption_m.group(1)} одн")
                month_consumption[f"{consumption_m.group(1)} расход"] = consumption_m.group(2).strip().replace(",", ".")
                month_consumption[f"{consumption_m.group(1)} инд"] = consumption_m.group(3).strip().replace(",", ".")
                month_consumption[f"{consumption_m.group(1)} одн"] = consumption_m.group(4).strip().replace(",", ".")

            consumption_data.append(month_consumption)

            month_meters = {"date": m.group(1)}
            for meter in m.group(3).split(";"):
                meter_m = meter_re.match(meter)
                if not meter_m:
                    print(f"Failed to parse metering data: {meter}")
                metering_fields.add(meter_m.group(1).strip())
                month_meters[meter_m.group(1).strip()] = meter_m.group(2).strip()

            metering_data.append(month_meters)

    with open(consuption_fname, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.DictWriter(csvfile, ["date"] + sorted(consumption_fields), dialect="excel")
        csv_writer.writeheader()
        for row in consumption_data:
            csv_writer.writerow(row)

    with open(metering_fname, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.DictWriter(csvfile, ["date"] + sorted(metering_fields), dialect="excel")
        csv_writer.writeheader()
        for row in metering_data:
            csv_writer.writerow(row)

    return 0


if __name__ == "__main__":
    exit(main("odpu.txt", "generated/consumption.csv", "generated/metering.csv"))