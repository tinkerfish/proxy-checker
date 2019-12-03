import argparse
import time
from threading import Thread
import requests
import math
import sys

timeout = 3
good_list = []


def get_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="ProxyCheck",
        usage="%(prog)s [-h] -i PROXY_FILE [-o OUT_FILE] -t THREADS",
        description="Test list of proxies for response and function",
    )
    parser.add_argument("-i", "--proxy_file", required=True, help="Proxy File Input")
    parser.add_argument("-o", "--output_file", help="Output File")
    parser.add_argument(
        "-t", "--threads", required=True, type=int, help="Number of threads to run on"
    )
    return parser.parse_args(argv)


def verify_proxy(proxy_list, thread_number):
    working_list = []
    for item in proxy_list:
        try:
            proxy_dict = {"http": item, "https": item}
            r = requests.get(
                "http://ipinfo.io/json", proxies=proxy_dict, timeout=timeout
            )
            response = r.json()
            ip = response["ip"]
            print(f"[Thread: {thread_number}] Current IP: {ip}")
            print(f"[Thread: {thread_number}] Proxy Active: {item}")
            print(
                f'[Thread: {thread_number}] Proxy Works: {True if ip == item.split(":")[0] else False}'
            )
            working_list.append(item)
        except Exception as e:
            print(f"[Thread: {thread_number}] Proxy Failed: {item}")
            print(f"[Thread: {thread_number}] Proxy Failed: {e}")

    print(f"[Thread: {thread_number}] Working Proxies: {len(working_list)}")
    good_list.extend(working_list)


def get_proxies(file):
    proxy_list = []
    for item in open(file, "r+").readlines():
        proxy_list.append(item.strip())
    return proxy_list


def setup(number_threads):
    thread_count = float(number_threads)
    proxy_list = get_proxies(args.proxy_file)
    amount = int(math.ceil(len(proxy_list) / thread_count))
    proxy_lists = [
        proxy_list[x : x + amount] for x in range(0, len(proxy_list), amount)
    ]
    if len(proxy_list) % thread_count > 0.0:
        proxy_lists[len(proxy_lists) - 1].append(proxy_list[len(proxy_list) - 1])
    return proxy_lists


def main(threads):
    start_time = time.time()
    lists = setup(threads)
    thread_list = []
    count = 0
    for item in lists:
        thread_list.append(Thread(target=verify_proxy, args=(item, count)))
        thread_list[len(thread_list) - 1].start()
        count += 1

    for x in thread_list:
        x.join()

    print(f"Working Proxies: {good_list}")

    with open("good_proxies.txt", "w") as f:
        for i in good_list:
            f.write(i + "\n")

    stop_time = time.time()
    print(f"Completed in {stop_time - start_time} seconds.")


if __name__ == "__main__":
    argvals = None
    args = get_args(argvals)
    main(args.threads)
