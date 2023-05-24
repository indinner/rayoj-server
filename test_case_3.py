import math


def calculate_combinations(n, m):
    # 初始化动态规划表格
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # 边界情况，当m为0时，C(n, 0)只有一种情况
    for i in range(n + 1):
        dp[i][0] = 1

    # 动态规划计算组合数
    for i in range(1, n + 1):
        for j in range(1, min(i, m) + 1):
            dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]

    return dp[n][m]


def count_multiples(t, k, test_cases):
    results = []

    for n, m in test_cases:
        count = 0

        for i in range(n + 1):
            for j in range(min(i, m) + 1):
                if calculate_combinations(i, j) % k == 0:
                    count += 1

        results.append(count)

    return results


# 读取输入
t, k = map(int, input().split())
test_cases = []

for _ in range(t):
    n, m = map(int, input().split())
    test_cases.append((n, m))

# 计算答案
answers = count_multiples(t, k, test_cases)

# 输出答案
for ans in answers:
    print(ans)
