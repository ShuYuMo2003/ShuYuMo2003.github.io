---
title: 「杂题记录」「Ynoi」Y-fast trie
date: 2021-01-19 15:35:06
tags:
 - Ynoi
 - 数据结构
categories:
 - 杂题记录
---



给定一个常数 $C$ ，维护一个集合 $S$ ，支持 $n$ 次操作：

- 插入 $x$，保证之前不存在 $x$。
- 删除 $x$ ，保证之前存在 $x$。

每次操作后输出 $\max_{i, j\in S, i \not = j}\limits{(i + j) \mod C}$。是指 $\mod C$ 意义下的最大值。

强制在线。

<!-- more -->

$n\le 5\times 10^5, 1 \le C \le 1073741823,0 \le x \le 1073741823$

## 分析

每个数字只能和两个数字匹配 可能成为最大值。