import json
import os
import subprocess
import time
import uuid
import ray
from flask import Flask, request
from flask_cors import cross_origin
from compile_run import compile_run_blueprint

app = Flask(__name__)
app.register_blueprint(compile_run_blueprint)

# 从环境变量获取Ray URL，如果没有设置，则使用默认值。
ray_url = os.environ.get("RAY_URL", 'ray://119.45.173.116:10001')


@app.route('/oj_run_v2', methods=['POST'])
@cross_origin(origins="*")
def oj_run_v2():

    is_ray_connected()

    data = json.loads(request.data)
    input_case = data['input_case']
    output_case = data['output_case']

    # 根据测试用例总数确定每个节点的用例数量。
    case_number = len(input_case)
    fund_number = 3 if case_number <= 10 else 5

    # 将测试用例分割成块。
    temp_input = split_list(input_case, fund_number)
    temp_output = split_list(output_case, fund_number)

    res_obj_id = [ray_oj.remote({**data, 'input_case': inp, 'output_case': out})
                  for inp, out in zip(temp_input, temp_output)]

    res = ray.get(res_obj_id)
    return json.dumps(res, ensure_ascii=False)


@app.route('/oj_run_v1', methods=['POST'])
@cross_origin(origins="*")
def oj_run_v1():
    data = json.loads(request.data)
    result = ray.get(ray_oj.remote(data))
    return json.dumps(result)


@ray.remote
def ray_oj(data):
    def get_filenames_by_language(language):
        """根据编程语言获取文件名。"""
        if language == 'python':
            return 'test.py', 'test.py'
        elif language in ['c++', 'cpp']:
            return 'Main.cpp', 'Main'
        raise ValueError(f"不支持的语言: {language}")

    def write_to_file(content, file_path):
        """将内容写入文件。"""
        with open(file_path, 'w') as file:
            file.write(content + '\n')

    def build_command(language, time_limit, memory_limit, test_dir, filename, result_type):
        """构建运行判题的命令。"""
        language_type = 'python3' if language == 'python' else 'cpp'
        cmd_template = (
            "python /home/acm-judge-module/judge/judge.py "
            "--language {language} --languageConfig /home/acm-judge-module/judge/language/ "
            "--file {test_dir}/{filename} --time {time} --memory {memory} "
            "--testDir {test_dir} --mode entire --type {result_type} "
            "--delete false --codeResultDir {test_dir}"
        )
        return cmd_template.format(
            language=language_type,
            test_dir=test_dir,
            filename=filename,
            time=time_limit,
            memory=memory_limit,
            result_type=result_type
        )

    def execute_command(cmd):
        """执行一个shell命令并返回输出。"""
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd, output=out, stderr=err)
        return out

    random_id = str(uuid.uuid1())
    test_dir = f'/testcase/{random_id}'
    os.makedirs(test_dir, exist_ok=True)

    language = data['language']
    filename, exec_filename = get_filenames_by_language(language)

    write_to_file(data['code'], os.path.join(test_dir, filename))
    for i, (input_case, output_case) in enumerate(zip(data['input_case'], data['output_case'])):
        write_to_file(input_case, os.path.join(test_dir, f'{i}.in'))
        write_to_file(output_case, os.path.join(test_dir, f'{i}.out'))

    cmd = build_command(language, data['time'], data['memory'], test_dir, exec_filename, data['result_type'])
    return execute_command(cmd)


def split_list(lst, n):
    """将列表分割成大小为n的块。"""
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def is_ray_connected():
    if not ray.is_initialized():
        ray.init(ray_url)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
