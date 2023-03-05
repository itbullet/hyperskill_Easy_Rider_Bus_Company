import json
import re
from datetime import datetime


def check_pattern(data, type1):
    if type1 == "stop_name":
        pattern = r"[A-Z][\w\s]+(Road|Avenue|Boulevard|Street)$"
    elif type1 == "stop_type":
        pattern = r"[SOF]?$"
    elif type1 == "a_time":
        pattern = r"[0-2][0-9]:[0-5][0-9]$"

    return bool(re.match(pattern, data))


def errors_summary(list_of_dicts):
    errors_dictionary = {}

    for dictionary in list_of_dicts:
        for key, val in dictionary.items():
            if key not in errors_dictionary:
                errors_dictionary.setdefault(key, 0)

            if key == "bus_id" and not isinstance(val, int):
                errors_dictionary["bus_id"] += 1

            elif key == "stop_id" and not isinstance(val, int):
                errors_dictionary["stop_id"] += 1

            elif key == "stop_name" and (not check_pattern(val, key) or not isinstance(val, str) or not len(val) > 1):
                errors_dictionary["stop_name"] += 1

            elif key == "next_stop" and not isinstance(val, int):
                errors_dictionary["next_stop"] += 1

            elif key == "stop_type" and (not check_pattern(val, key) or not isinstance(val, str) or len(val) > 1):
                errors_dictionary["stop_type"] += 1

            elif key == "a_time" and (not check_pattern(val, key) or not isinstance(val, str) or not len(val) > 1):
                errors_dictionary["a_time"] += 1
    errors_sum = sum(errors_dictionary.values())
    if errors_sum > 0:
        print(f"Type and required field validation: {errors_sum} errors")
        print("\n".join([f"{key}: {val}" for key, val in errors_dictionary.items() if val > 0]))
        return False
    else:
        return True


def count_stops(list_of_dicts):
    buses_stops_dictionary = {}

    for dictionary in list_of_dicts:
        if dictionary.get("bus_id") not in buses_stops_dictionary:
            buses_stops_dictionary.setdefault(dictionary.get("bus_id"), 1)
        else:
            buses_stops_dictionary[dictionary.get("bus_id")] += 1

    stops_sum = sum(buses_stops_dictionary.values())
    if stops_sum > 0:
        print(f"Line names and number of stops:")
        print("\n".join([f"bus_id: {key}, stops: {val}" for key, val in buses_stops_dictionary.items() if val > 0]))


def check_route(list_of_dicts):
    routes_stops_dictionary = {}
    report_dictionary = {}

    for dictionary in list_of_dicts:
        if dictionary.get("bus_id") not in routes_stops_dictionary:
            routes_stops_dictionary.setdefault(dictionary.get("bus_id"), []).append((dictionary.get("stop_type"),
                                                                                     dictionary.get("stop_name")))
        else:
            routes_stops_dictionary[dictionary.get("bus_id")].append(
                (dictionary.get("stop_type"), dictionary.get("stop_name")))

    for key, val in routes_stops_dictionary.items():
        if not all(any(stop_type in tup for tup in val) for stop_type in ["S", "F"]):
            print(f"There is no start or end stop for the line: {key}.")
            break

    list_of_streets = []
    for dictionary in list_of_dicts:
        if dictionary["stop_type"] == "S":
            if not report_dictionary.get("Start stops"):
                report_dictionary.setdefault("Start stops", []).append(dictionary.get("stop_name"))
            elif dictionary.get("stop_name") not in report_dictionary["Start stops"]:
                report_dictionary.get("Start stops").append(dictionary.get("stop_name"))

        elif dictionary["stop_type"] == "F":
            if not report_dictionary.get("Finish stops"):
                report_dictionary.setdefault("Finish stops", []).append(dictionary.get("stop_name"))
            elif dictionary.get("stop_name") not in report_dictionary["Finish stops"]:
                report_dictionary.setdefault("Finish stops", []).append(dictionary.get("stop_name"))

        list_of_streets.append(dictionary.get("stop_name"))

    transfer_stops = set([street for street in list_of_streets if list_of_streets.count(street) > 1])
    report_dictionary["Transfer stops"] = list(transfer_stops)

    # for key in ["Start stops", "Transfer stops", "Finish stops"]:
    #     val = report_dictionary[key]
    #     print(f"{key}: {len(val)} {sorted(val)}")

    return report_dictionary


def arrival_time_test(list_of_dicts):
    time_format = "%H:%M"
    bus_id_dictionary = {}

    for dictionary in list_of_dicts:
        bus_id = dictionary.get('bus_id')
        next_stop = dictionary.get('next_stop')
        time_current_stop = datetime.strptime(dictionary.get('a_time'), time_format)
        if not bus_id_dictionary.get(bus_id):
            for dict_item in list_of_dicts:
                time_next_stop = datetime.strptime(dict_item['a_time'], time_format)
                if dict_item['bus_id'] == bus_id and dict_item['stop_id'] == next_stop and time_next_stop < time_current_stop:
                    next_stop_id = dict_item.get('bus_id')
                    next_stop_name = dict_item.get('stop_name')
                    bus_id_dictionary.setdefault(bus_id, {'stop_id': next_stop_id, 'stop_name': next_stop_name})

    print("Arrival time test:")
    if bus_id_dictionary:
        for key, dictionary in bus_id_dictionary.items():
            bus_id = key
            stop_name = dictionary.get('stop_name')
            print(f"bus_id line {bus_id}: wrong time on station {stop_name}")
    else:
        print("OK")


def on_demand_stop_test(report_dictionary, list_of_dicts):
    combined_list = []
    wrong_stop_type = []
    for values in report_dictionary.values():
        combined_list.extend(values)
    combined_list = list(set(combined_list))

    for dictionary in list_of_dicts:
        stop_name = dictionary.get('stop_name')
        if all([stop_name in combined_list, stop_name not in wrong_stop_type, dictionary.get('stop_type') == 'O']):
            wrong_stop_type.append(stop_name)

    print("On demand stops test:")
    if wrong_stop_type:
        print(f"Wrong stop type: {sorted(wrong_stop_type)}")
    else:
        print("OK")


if __name__ == "__main__":
    string = input()

    list_of_dictionaries = json.loads(string)
    if errors_summary(list_of_dictionaries):
        # count_stops(list_of_dictionaries)
        report_dict = check_route(list_of_dictionaries)
        on_demand_stop_test(report_dict, list_of_dictionaries)
        # arrival_time_test(list_of_dictionaries)
