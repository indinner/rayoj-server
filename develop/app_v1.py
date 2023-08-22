from time import sleep

from flask import Flask, jsonify, request
import subprocess
import json
import ray
import uuid

from flask_cors import cross_origin

app = Flask(__name__)
# 启动Ray.
ray.init('ray://119.45.173.116:10001')


# ray.init(address='auto', _node_ip_address='119.45.71.218')
# ray.init(address='119.45.71.218:6379',_redis_password='5241590000000000')

@ray.remote
class MyActor:
    def __init__(self):
        self.value = 0

    def ray_oj(self, data):
        code = data['code']  # 执行代码
        input_case = data['input_case']  # 输入样例,数组
        output_case = data['output_case']  # 输出样例,数组
        time = data['time']  # 时间限制
        memory = data['memory']  # 空间限制
        language = data['language']  # 语言
        result_type = data['result_type']  # 返回结果类型，json str
        random_id = str(uuid.uuid1())
        subprocess.call('mkdir /testcase/' + random_id, shell=True)  # 创建一个测试文件夹
        subprocess.call('echo "' + code + '" > /testcase/' + random_id + '/test.py', shell=True)  # 创建待测试文件
        for i in range(0, len(input_case)):  # 创建测试用例文件
            subprocess.call('echo "' + input_case[i] + '" > /testcase/' + random_id + '/' + str(i) + '.in', shell=True)
            subprocess.call('echo "' + output_case[i] + '" > /testcase/' + random_id + '/' + str(i) + '.out',
                            shell=True)
            cmd = ''
            if language == 'python':
                cmd = "python /home/acm-judge-module/judge/judge.py --language python3 --languageConfig /home/acm-judge-module/judge/language/ --file /testcase/" + random_id + "/test.py --time " + str(
                    time) + " --memory " + str(
                    memory) + " --testDir /testcase/" + random_id + " --mode entire --type " + result_type + " --delete false --codeResultDir " + "/testcase/" + random_id,
        res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, text=True)
        (out, err) = res.communicate()
        pass
        return out


my_actor = MyActor.remote()


@app.route('/oj_run_v2', methods=['POST'])
@cross_origin(origins="*")
def oj_run_v2():  # put application's code here
    data = json.loads(request.data)
    code = data['code']  # 执行代码
    input_case = data['input_case']  # 获取传进来的测试用例
    output_case = data['output_case']  # 获取传进来的测试用例
    res_obj_id = []

    # 判断测试用例数量，小于等于10则使用每节点每次判一个测试用例的逻辑
    # 大于10则每节点分配多个测试用例判题
    case_number = len(input_case)
    fund_number = 1
    if case_number <= 10:
        fund_number = 3
    else:
        fund_number = 5

    # 切割测试用例
    temp_input = fund(input_case, fund_number)
    temp_output = fund(output_case, fund_number)

    for i in range(0, len(temp_input)):
        data['input_case'] = temp_input[i]
        data['output_case'] = temp_output[i]
        kid = ray_oj.remote(data)
        res_obj_id.append(kid)
    res = ray.get(res_obj_id)
    # print(type(res))
    return ''.join(json.dumps(res, ensure_ascii=False))


# v1接口，所有测试用例放在一个沙盒进行测试
@app.route('/oj_run_v1', methods=['POST'])
@cross_origin(origins="*")
def oj_run_v1():  # put application's code here
    data = json.loads(request.data)
    kid = ray_oj.remote(data)
    res = ray.get(kid)
    return ''.join(res)


def fund(list_emp, n):
    resules = []
    for i in range(0, len(list_emp), n):
        temp = list_emp[i:i + n]
        resules.append(temp)
    return resules


@ray.remote
def ray_oj(data):
    code = data['code']  # 执行代码
    input_case = data['input_case']  # 输入样例,数组
    output_case = data['output_case']  # 输出样例,数组
    print("input_case", input_case)
    print("output_case", output_case)

    time = data['time']  # 时间限制
    memory = data['memory']  # 空间限制
    language = data['language']  # 语言
    result_type = data['result_type']  # 返回结果类型，json str
    random_id = str(uuid.uuid1())
    subprocess.call('mkdir /testcase/' + random_id, shell=True)  # 创建一个测试文件夹
    subprocess.call('echo "' + code + '" > /testcase/' + random_id + '/test.py', shell=True)  # 创建待测试文件
    for i in range(0, len(input_case)):  # 创建测试用例文件
        subprocess.call('echo "' + input_case[i] + '" > /testcase/' + random_id + '/' + str(i) + '.in', shell=True)
        subprocess.call('echo "' + output_case[i] + '" > /testcase/' + random_id + '/' + str(i) + '.out', shell=True)
        cmd = ''
        if language == 'python':
            cmd = "python /home/acm-judge-module/judge/judge.py --language python3 --languageConfig /home/acm-judge-module/judge/language/ --file /testcase/" + random_id + "/test.py --time " + str(
                time) + " --memory " + str(
                memory) + " --testDir /testcase/" + random_id + " --mode entire --type " + result_type + " --delete false --codeResultDir " + "/testcase/" + random_id,
    res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, text=True)
    # print(cmd)
    (out, err) = res.communicate()
    pass
    return out


if __name__ == '__main__':
    app.run(host='0.0.0.0')
