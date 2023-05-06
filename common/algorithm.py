import time
from math import sqrt


def similarity(data):
    # 1 构造物品：物品的共现矩阵
    N = {}  # 喜欢物品i的总⼈数
    C = {}  # 喜欢物品i也喜欢物品j的⼈数
    for user, item in data.items():
        for i, score in item.items():
            N.setdefault(i, 0)
            N[i] += 1
            C.setdefault(i, {})
            for j, scores in item.items():
                if j != i:
                    C[i].setdefault(j, 0)
                    C[i][j] += 1
    print("---1.构造的共现矩阵---")
    print('N:', N)
    print('C', C)
    # 2 计算物品与物品的相似矩阵
    W = {}
    for i, item in C.items():
        W.setdefault(i, {})
        for j, item2 in item.items():
            W[i].setdefault(j, 0)
            W[i][j] = C[i][j] / sqrt(N[i] * N[j])
    print("---2.构造的相似矩阵---")
    print(W)
    return W


def recommend_list(data, sames_matrix, user, depth=3, count=10):
    """
    # 3.根据⽤户的历史记录，给⽤户推荐物品
    :param data: 用户数据
    :param sames_matrix: 相似矩阵
    :param user: 推荐的用户
    :param depth: 相似的k个物品
    :param count: 推荐物品数量
    :return:
    """

    rank = {}
    # 获得⽤户user历史记录，如A⽤户的历史记录为{'唐伯虎点秋香': 5, '逃学威龙1': 1, '追龙': 2}
    for i, score in data[user].items():
        # 获得与物品i相似的k个物品
        for j, w in sorted(sames_matrix[i].items(), key=lambda x: x[1], reverse=True)[0:depth]:
            # 该相似的物品不在⽤户user的记录⾥
            if j not in data[user].keys():
                rank.setdefault(j, 0)
                # 预测兴趣度 = 评分 × 相似度
                rank[j] += float(score) * w
    print("---3.获取推荐列表---")
    print(sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:count])
    return sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:count]


if __name__ == '__main__':
    # ⽤户，电影，评分
    data = {
        '用户A': {'唐伯虎点秋香': 5, '逃学威龙1': 1, '追龙': 2},
        '用户B': {'唐伯虎点秋香': 4, '喜欢你': 2, '暗战': 3.5},
        '用户C': {'逃学威龙1': 2, '他人笑我太疯癫': 4},
        '用户D': {'喜欢你': 4, '暗战': 3},
        '用户E': {'逃学威龙1': 4, '他人笑我太疯癫': 3}
    }
    st = time.time()
    W = similarity(data)  # 计算物品相似矩阵
    ed = time.time()
    print(f"耗时：{ed - st}")
    print(recommend_list(data, W, '用户A', 3, 10))  # 推荐
    ed2 = time.time()
    print(f"耗时：{ed2 - ed}")
