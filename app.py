import json
import os
import subprocess
import uuid

import ray
from flask import Flask, request
from flask_cors import cross_origin

app = Flask(__name__)
# 启动Ray.
ray.init('ray://119.45.71.218:10001')

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
    def write_to_file(content, file_path):
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            print("内容已成功写入文件。")
        except IOError:
            print("无法写入文件：{}".format(file_path))

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
    filename = ''
    filename_=''
    if language == 'python':
        filename = 'test.py'
        filename_='test.py'
    elif language == 'c++':
        filename = 'Main.cpp'
        filename_='Main'
    #subprocess.call('echo "' + code + '" > /testcase/' + random_id + '/' + filename, shell=True)  # 创建待测试文件
    write_to_file(code,'/testcase/' + random_id + '/' + filename)
    for i in range(0, len(input_case)):  # 创建测试用例文件
        #subprocess.call('echo "' + input_case[i] + '" > /testcase/' + random_id + '/' + str(i) + '.in', shell=True)
        #subprocess.call('echo "' + output_case[i] + '" > /testcase/' + random_id + '/' + str(i) + '.out', shell=True)
        write_to_file(input_case[i], '/testcase/' + random_id + '/' + str(i) + '.in')
        write_to_file(output_case[i], '/testcase/' + random_id + '/' + str(i) + '.out')

        language_type = ''
        if language == 'python':
            language_type = 'python3'
        elif language == 'c++':
            language_type = 'cpp'
        cmd = "python /home/acm-judge-module/judge/judge.py --language " + language_type + " --languageConfig /home/acm-judge-module/judge/language/ --file /testcase/"  + "/" + filename_ + " --time " + str(
            time) + " --memory " + str(
            memory) + " --testDir /testcase/" + random_id + " --mode entire --type " + result_type + " --delete false --codeResultDir " + "/testcase/" + random_id
    res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, text=True)
    # print(cmd)
    (out, err) = res.communicate()
    pass
    return out


if __name__ == '__main__':
    app.run(host='0.0.0.0')
