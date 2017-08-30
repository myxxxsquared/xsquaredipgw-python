#!/usr/bin/env python3

"""
ipgw.py xsquredipgw-python xsquredipgw北京大学网关连接-python版

Copyright (C) 2017 Zhang Wenjie (wenjiez696@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import getpass
from argparse import ArgumentParser
from collections import OrderedDict
from configparser import ConfigParser
import requests


IPGW_REQUEST_URL = "https://its.pku.edu.cn/cas/ITSClient"
IPGW_REQUEST_DATA = {"lang": "",
                     "app": "myxxxsquared_IPGW_PYTHON"}
IPGW_REQUEST_HEADER = {"Host": "its.pku.edu.cn",
                       "User-Agent": "myxxxsquared_IPGW_PYTHON",
                       "Endpoint": "POST https://its.pku.edu.cn/cas/ITSClient",
                       "Content-Type": "application/x-www-form-urlencoded",
                       "Accept": "*/*"}

def ipgwRequest(body: dict) -> dict:
    """ 发送请求到网关 """
    body = dict(body)
    body.update(IPGW_REQUEST_DATA)
    try:
        response = requests.post(IPGW_REQUEST_URL, data=body, headers=IPGW_REQUEST_HEADER)
        response.raise_for_status()
        return response.json(object_pairs_hook=OrderedDict)
    except requests.exceptions.RequestException as ex:
        return {"error": str(ex)}

def ipgwConnect(**kwargs) -> dict:
    """ 连接 """
    return ipgwRequest({"cmd": "open",
                        "username": kwargs["user"],
                        "password": kwargs["password"],
                        "iprange": "yes" if kwargs["fee"] else "no"
                       })

def ipgwDisconnect(**kwargs) -> dict:
    """ 断开连接 """
    return ipgwRequest({"cmd": "close"})

def ipgwDisconnectAll(**kwargs) -> dict:
    """ 断开全部连接 """
    return ipgwRequest({"cmd": "closeall",
                        "username": kwargs["user"],
                        "password": kwargs["password"],
                       })

def ipgwGetConnections(**kwargs) -> dict:
    """ 获取在线连接 """
    return ipgwRequest({"cmd": "getconnections",
                        "username": kwargs["user"],
                        "password": kwargs["password"],
                       })

def ipgwDisConnectIp(**kwargs) -> dict:
    """ 断开某个连接 """
    return ipgwRequest({"cmd": "disconnect",
                        "username": kwargs["user"],
                        "password": kwargs["password"],
                        "ip": kwargs["ip"]
                       })

IPGW_CMD_CHOICES = ["conn", "disconn", "disconnall", "getconns", "disconnip"]
IPGW_CMD_HELP = "指示需要进行的操作：conn 连接，" + \
                "disconn 断开，disconnall 断开全部，" + \
                "getconns 获取当前在线连接，disconnip 断开指定ip的连接。 "
IPGW_DESCRIPTION = """ PKUIPGW Python myxxxsquared https://github.com/myxxxsquared """

def main():
    """ 主函数 """
    argparser = ArgumentParser(description=IPGW_DESCRIPTION)
    argparser.add_argument("cmd", type=str, help=IPGW_CMD_HELP, choices=IPGW_CMD_CHOICES)
    argparser.add_argument("-c", "--config_file", type=str, help="配置文件")
    argparser.add_argument("-u", "--user", type=str, help="用户名")
    argparser.add_argument("-p", "--password", type=str, help="密码")
    argparser.add_argument("-f", "--fee", type=bool, help="指示是否连接到收费网")
    argparser.add_argument("--ip", type=str, help="断开连接的IP地址")
    args = argparser.parse_args()

    configparser = ConfigParser()
    configparser.read_dict({"PKUIPGW": {"user": "", "password": "", "fee": 0}})

    if args.config_file:
        configparser.read_file(open(args.config_file))
    else:
        config_file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pkuipgw.conf")
        if os.path.exists(config_file_name):
            configparser.read(config_file_name)
        else:
            configparser.read("/etc/pkuipgw.conf")


    kwargs = {}
    kwargs["user"] = args.user or configparser.get("PKUIPGW", "user")
    kwargs["password"] = args.password or configparser.get("PKUIPGW", "password")
    kwargs["fee"] = bool(int(configparser.get("PKUIPGW", "fee"))) if args.fee is None else args.fee
    kwargs["ip"] = args.ip

    if not kwargs["user"] and args.cmd != "disconn":
        kwargs["user"] = input("用户:")
    if not kwargs["password"] and args.cmd != "disconn":
        kwargs["password"] = getpass.getpass("密码:")
    if args.cmd == "disconnip" and not kwargs["ip"]:
        kwargs["ip"] = input("IP:")

    funcselect = {
        "conn": ipgwConnect,
        "disconn": ipgwDisconnect,
        "disconnall": ipgwDisconnectAll,
        "getconns": ipgwGetConnections,
        "disconnip": ipgwDisConnectIp
    }

    results = funcselect[args.cmd](**kwargs)

    for result in results.items():
        print("{} : {}".format(result[0], result[1]))

__all__ = [
    "ipgwRequest",
    "ipgwConnect",
    "ipgwDisconnect",
    "ipgwDisconnectAll",
    "ipgwGetConnections",
    "ipgwDisConnectIp",
]

if __name__ == "__main__":
    main()
