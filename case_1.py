def convert_to_base(n, b):
    digits = "0123456789ABCDEF"
    result = ''

    # 处理特殊情况，当n为0时直接返回0
    if n == 0:
        return '0'

    # 将n转换为b进制，逆序存储在result字符串中
    while n > 0:
        result = digits[n % b] + result
        n //= b

    # 如果b为16进制，添加前缀'0X'
    if b == 16:
        result = '0X' + result

    return result

T = int(input())

for _ in range(T):
    n, b = map(int, input().split())
    print(convert_to_base(n, b))
