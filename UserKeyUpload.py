import requests
import json


def SetJson(hash):
    # 合约部署接口的URL
    url = 'http://plus.ismartchain.cn/port5002/WeBASE-Front/trans/handleWithSign'
    # 请求体数据
    transaction_data = {
        "groupId": "1",
        "signUserId": "cf771c12a654468ab8dc2898df988798",
        "contractName": "UploadUserKey",
        "contractPath": "/",
        "version": "",
        "funcName": "setHash",
        "funcParam": [hash],
        "contractAddress": "0xe4e885842a9470c0ee331d270e95d70b27d4218b",
        "contractAbi": [{"constant": True, "inputs": [], "name": "hash", "outputs": [{"name": "", "type": "string"}],
                         "payable": False, "stateMutability": "view", "type": "function"},
                        {"constant": False, "inputs": [{"name": "_hash", "type": "string"}], "name": "setHash",
                         "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"},
                        {"constant": True, "inputs": [], "name": "getHash", "outputs": [{"name": "", "type": "string"}],
                         "payable": False, "stateMutability": "view", "type": "function"},
                        {"inputs": [], "payable": False, "stateMutability": "nonpayable", "type": "constructor"}],
        "useAes": False,
        "useCns": False,
        "cnsName": ""
    }

    # 将数据转换为JSON格式
    json_data = json.dumps(transaction_data)

    # 发送POST请求
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json_data, headers=headers)

    # 检查请求是否成功
    if response.status_code == 200:
        # 请求成功，解析返回的数据
        print("Upload Success. The Transaction Info:", response.text)
    else:
        # 请求失败，打印错误信息
        print('Failed to call API:', response.status_code, response.text)
