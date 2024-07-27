import json

import requests

url = "http://8.137.90.234:5555/oj_compiler_run"

code = '''
//下面是一个输入输出的例子, 仅供参考
#include <iostream>
using namespace std;
int main() {
    // 输入
    int num;
    cout << "请输入一个整数：";
    cin >> num;
	
	int i=0;
	for(i=0;i<1000000000;i++){
    	cout << "输入的整数是：" << num << endl;
	}

    // 输出
    cout << "输入的整数是：" << num << endl;

    return 0;
}
'''

payload = {
    "code":code,
    "language": "c++",
    "case_input": "123"
}
print(payload)
headers = {'Content-Type': 'application/json'}

res=requests.post(url=url,data=json.dumps(payload),headers=headers)
print(res.content)