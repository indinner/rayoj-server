# OJ代码编译并运行模块
import json
import subprocess
import os
import shlex
import uuid
import ray
import time
import resource
from flask import Blueprint, request
from flask_cors import cross_origin
from src.main import is_ray_connected

compile_run_blueprint = Blueprint('compile_run_blueprint', __name__)


@compile_run_blueprint.route('/oj_compiler_run', methods=['POST'])
@cross_origin(origins="*")
def oj_compiler_run():

    is_ray_connected()

    data = json.loads(request.data)
    code = data['code']
    language = data['language']
    case_input = data['case_input']
    # 启动远程任务
    future = oj_compile_run.remote(code, case_input, language)
    # 等待远程任务完成并获取结果
    state, output, err, run_time, memory_usage = ray.get(future)
    if isinstance(output, bytes):
        output = output.decode('utf-8', errors='replace')  # 解码字节串

    if isinstance(err, bytes):
        err = err.decode('utf-8', errors='replace')  # 解码字节串
    result = {
        "state": state,
        "output": output,
        "err": err,
        "run_time": run_time,  # 运行时间
        "memory_usage": memory_usage  # 内存使用
    }
    print(result)
    return json.dumps(result, ensure_ascii=False)


@ray.remote
def oj_compile_run(code, case_input, language):
    # 编译C++代码
    def compile_cpp(source_code_file, executable_file):
        compile_command = f"g++ -o {executable_file} {source_code_file}"
        compile_process = subprocess.run(shlex.split(compile_command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return compile_process.returncode, compile_process.stdout, compile_process.stderr

    # 运行编译后的可执行文件
    def run_executable(executable_file, input_text):
        start_time = time.time()
        start_memory = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        run_process = subprocess.run(executable_file, input=input_text.encode(), stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, timeout=5)
        end_time = time.time()
        end_memory = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        total_time = end_time - start_time
        memory_usage = end_memory - start_memory
        return run_process.returncode, run_process.stdout.decode(), run_process.stderr.decode(), total_time, memory_usage

    # 执行Python代码
    def execute_python(source_code_file, input_text):
        start_time = time.time()
        start_memory = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        run_command = f"python {source_code_file}"
        run_process = subprocess.run(shlex.split(run_command), input=input_text.encode(), stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, timeout=5)
        end_time = time.time()
        end_memory = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        total_time = end_time - start_time
        memory_usage = end_memory - start_memory
        return run_process.returncode, run_process.stdout.decode(), run_process.stderr.decode(), total_time, memory_usage

    # 运行
    if language == 'python':
        python_file_name = f"temp_code_{uuid.uuid4().hex}.py"
        with open(python_file_name, 'w') as file:
            file.write(code)
        python_status, python_out, python_err, python_time, python_memory = execute_python(python_file_name, case_input)
        os.remove(python_file_name)
        return python_status, python_out, python_err, python_time, python_memory
    elif language == 'c++':
        cpp_file_name = f"temp_code_{uuid.uuid4().hex}.cpp"
        with open(cpp_file_name, 'w') as file:
            file.write(code)
        executable_name = f"temp_executable_{uuid.uuid4().hex}"
        compile_status, compile_out, compile_err = compile_cpp(cpp_file_name, executable_name)
        if compile_status == 0:
            run_status, run_out, run_err, cpp_time, cpp_memory = run_executable(f"./{executable_name}", case_input)
            os.remove(cpp_file_name)
            os.remove(executable_name)
            return run_status, run_out, run_err, cpp_time, cpp_memory
        else:
            os.remove(cpp_file_name)
            compile_status = 7
            return compile_status, compile_out, compile_err, 0, 0  # 这里假设编译失败不消耗时间和内存
