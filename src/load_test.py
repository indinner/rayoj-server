import requests
import concurrent.futures
import time

# 请求的URL和请求体
url = "http://8.137.90.234:5555/oj_compiler_run"
payload = {
    "code":'''
    //下面是一个输入输出的例子, 仅供参考
#include <iostream>
using namespace std;
int main() {
    // 输入
    int num;
    cout << "请输入一个整数：";
    cin >> num;
	
	int i=0;
	for(i=0;i<1000000;i++){
    	cout << "输入的整数是：" << num << endl;
	}

    // 输出
    cout << "输入的整数是：" << num << endl;

    return 0;
}
    ''',
    "language":"c++",
    "case_input":"123"
}
headers = {'Content-Type': 'application/json'}


# 发送单个POST请求的函数
def send_post_request():
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code, response.text


# 执行压测的函数
def run_load_test(num_requests, num_threads):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(send_post_request) for _ in range(num_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    return results


# 压测参数
num_requests = 1  # 总请求数
num_threads = 1  # 并发线程数

# 运行压测并记录时间
start_time = time.time()
results = run_load_test(num_requests, num_threads)
end_time = time.time()

# 打印结果和耗时
print(f"总耗时: {end_time - start_time} 秒")
for status_code, response_text in results:
    print(f"状态码: {status_code}, 响应: {response_text}")
