# OJ代码编译并运行模块
import json
import subprocess
import os
import shlex
import uuid
import ray
from flask import Blueprint, request
from flask_cors import cross_origin

compile_run_blueprint = Blueprint('compile_run_blueprint', __name__)


# 编译并运行代码
@compile_run_blueprint.route('/oj_compiler_run', methods=['POST'])
@cross_origin(origins="*")
def oj_compiler_run():
    data = json.loads(request.data)
    code = data['code']
    language = data['language']
    case_input = data['case_input']
    # 启动远程任务
    future = oj_compile_run.remote(code, case_input, language)
    # 等待远程任务完成并获取结果
    state, output, err = ray.get(future)
    if isinstance(output, bytes):
        output = output.decode('utf-8', errors='replace')  # 解码字节串

    if isinstance(err, bytes):
        err = err.decode('utf-8', errors='replace')  # 解码字节串
    result = {
        "state": state,
        "output": output,
        "err": err
    }
    print(result)
    return json.dumps(result, ensure_ascii=False)


@ray.remote
def oj_compile_run(code, case_input, language):
    # 编译C++代码
    def compile_cpp(source_code_file, executable_file):
        # 构造编译命令
        compile_command = f"g++ -o {executable_file} {source_code_file}"
        # 执行编译命令
        compile_process = subprocess.run(shlex.split(compile_command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 返回编译结果代码，标准输出和标准错误输出
        return compile_process.returncode, compile_process.stdout, compile_process.stderr

    # 运行编译后的可执行文件
    def run_executable(executable_file, input_text):
        # 使用提供的输入运行可执行文件
        run_process = subprocess.run(executable_file, input=input_text.encode(), stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, timeout=5)
        # 返回运行结果代码，标准输出和标准错误输出（解码后的字符串）
        return run_process.returncode, run_process.stdout.decode(), run_process.stderr.decode()

    # 执行Python代码
    def execute_python(source_code_file, input_text):
        # 构造运行Python代码的命令
        run_command = f"python {source_code_file}"
        # 执行Python代码
        run_process = subprocess.run(shlex.split(run_command), input=input_text.encode(), stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, timeout=5)
        # 返回运行结果代码，标准输出和标准错误输出（解码后的字符串）
        return run_process.returncode, run_process.stdout.decode(), run_process.stderr.decode()

    if language == 'python':
        # 将Python代码写入一个临时文件
        python_file_name = f"temp_code_{uuid.uuid4().hex}.py"
        with open(python_file_name, 'w') as file:
            file.write(code)
        # 执行Python代码
        python_status, python_out, python_err = execute_python(python_file_name, case_input)
        # 清理临时文件
        os.remove(python_file_name)
        return python_status, python_out, python_err
    elif language == 'c++':
        # 将C++代码写入一个临时文件
        cpp_file_name = f"temp_code_{uuid.uuid4().hex}.cpp"
        with open(cpp_file_name, 'w') as file:
            file.write(code)

        # 编译C++代码
        executable_name = f"temp_executable_{uuid.uuid4().hex}"
        compile_status, compile_out, compile_err = compile_cpp(cpp_file_name, executable_name)
        if compile_status == 0:
            # 如果编译成功，则运行C++可执行文件
            run_status, run_out, run_err = run_executable(f"./{executable_name}", case_input)
            # 清理临时文件
            os.remove(cpp_file_name)
            os.remove(executable_name)
            return run_status, run_out, run_err
        else:
            # 清理临时文件
            os.remove(cpp_file_name)
            # 编译错误，返回编译信息
            compile_status = 7
            return compile_status, compile_out, compile_err
