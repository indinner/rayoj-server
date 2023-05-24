# 读取输入的字符串
input_string = input()
strings = input_string.split(' ')

longest = ''
for string in strings:
    if len(string) > len(longest):
       longest = string
# 输出结果
print(longest)
