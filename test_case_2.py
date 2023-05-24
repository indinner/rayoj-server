# 计算组合数
def calculate_combinations(n, m):
    numerator = 1
    denominator = 1
    for i in range(m):
        numerator *= (n - i)
        denominator *= (i + 1)
    return numerator // denominator

# 计算满足条件的对数
def count_multiples(n, m, k):
    count = 0
    for i in range(n + 1):
        for j in range(min(i, m) + 1):
            if (i * j) % k == 0:
                count += 1
    return count

# 主函数
if __name__ == '__main__':
    t, k = map(int, input().split())
    for _ in range(t):
        n, m = map(int, input().split())
        result = count_multiples(n, m, k)
        print(result)
