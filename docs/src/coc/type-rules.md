# 类型规则

构造演算拥有一个极其丰富的类型系统，它将项、类型和种类统一到单一的语法范畴中。这里给出的类型规则捕捉了依赖类型、宇宙多态性以及约束求解的本质——正是这些特性使得我们的实现既强大又复杂。

与更简单的类型系统不同，CoC 的类型规则必须同时处理多层抽象。项可以依赖于其他项（函数），类型可以依赖于项（依赖类型），类型可以依赖于类型（多态性），甚至种类也可以通过宇宙约束依赖于项。

## 符号词汇表

构造演算使用广泛的形式化符号来捕捉项、类型和宇宙之间的复杂关系。本词汇表提供了一份参考，用于理解类型规则中使用的符号和概念。

### 核心符号

- **\\( \Gamma \\)**（Gamma）：上下文或环境，用于跟踪哪些变量在作用域内及其类型
- **\\( \vdash \\)**（turnstile）：判断符号，读作“证明”或“蕴涵”
- **\\( \Pi \\)**（Pi）：依赖函数类型（`A -> B` 的泛化，其中结果类型可以依赖于输入值）
- **\\( \lambda \\)**（lambda）：函数抽象（创建一个函数）
- **\\( \equiv \\)**：定义性相等（根据计算规则被视为“相同”的两个项）
- **\\( \doteq \\)**：合一约束（询问两个项是否可以相等）
- **\\( \leadsto \\)**：约束求解（产生约束的解）

### 判断形式

- **\\( \Gamma \vdash t : T \\)**：“在上下文 Gamma 中，项 t 具有类型 T”
- **\\( \Gamma \vdash T : \text{Type}_i \\)**：“T 是一个位于宇宙层级 i 中的类型”
- **\\( \Gamma \vdash C \\)**：“约束 C 在上下文 Gamma 中成立”
- **\\( \Gamma \vdash s \equiv t : T \\)**：“项 s 和 t 在类型 T 上可转换”

### 类型系统概念

- **宇宙层级**：类型位于宇宙中（`Type_0`、`Type_1` 等），以避免逻辑悖论
- **依赖类型**：可以依赖于值的类型（如“长度为 n 的列表”）
- **元变量**：我们的约束求解器试图求解的未知量（写作 `?α`）
- **替换**：用值替换变量，写作 `t[s/x]`（在 t 中用 s 替换 x）
- **正性**：对归纳类型的一种限制，以确保其良基性

### 记号约定

- **上划线**：\\( \overline{x} \\) 表示“一系列 x”（如 x₁、x₂、x₃、……）
- **方括号**：\\( [s/x] \\) 表示用 s 替换 x
- **下标**：\\( \text{Type}_i \\) 指代宇宙层级
- **新变量**：当我们说“fresh(α)”时，指的是一个尚未使用过的全新变量

## 核心判断形式

CoC 类型系统使用多种判断形式，它们以复杂的方式相互作用：

**类型判断**：\\( \Gamma \vdash t : T \\) 断言在上下文 \\( \Gamma \\) 中，项 \\( t \\) 具有类型 \\( T \\)

**宇宙判断**：\\( \Gamma \vdash T : \text{Type}_i \\) 断言 \\( T \\) 是位于宇宙 \\( i \\) 中的类型

**约束判断**：\\( \Gamma \vdash C \\) 断言约束 \\( C \\) 在上下文 \\( \Gamma \\) 中成立

**转换判断**：\\( \Gamma \vdash s \equiv t : T \\) 断言 \\( s \\) 和 \\( t \\) 在类型 \\( T \\) 上可转换

## 变量和常量规则

上下文中的变量查找：

\\[ \frac{x : T \in \Gamma}{\Gamma \vdash x : T} \text{(T-Var)} \\]

带有显式层级约束的宇宙层级：

\\[ \frac{i < j}{\Gamma \vdash \text{Type}_i : \text{Type}_j} \text{(T-Univ)} \\]

其类型已知的原始常量：

\\[ \frac{}{\Gamma \vdash \text{Nat} : \text{Type}_0} \text{(T-Nat)} \\]

\\[ \frac{}{\Gamma \vdash 0 : \text{Nat}} \text{(T-Zero)} \\]

\\[ \frac{}{\Gamma \vdash \text{succ} : \text{Nat} \to \text{Nat}} \text{(T-Succ)} \\]

## 函数类型和抽象

依赖函数类型（Pi 类型）：

\\[ \frac{\Gamma \vdash A : \text{Type}\_i \quad \Gamma, x : A \vdash B : \text{Type}\_j}{\Gamma \vdash \Pi x : A. B : \text{Type}_{\text{max}(i,j)}} \text{(T-Pi)} \\]

带有依赖类型的 Lambda 抽象：

\\[ \frac{\Gamma, x : A \vdash t : B \quad \Gamma \vdash \Pi x : A. B : \text{Type}_i}{\Gamma \vdash \lambda x : A. t : \Pi x : A. B} \text{(T-Lam)} \\]

带有替换的函数应用：

\\[ \frac{\Gamma \vdash f : \Pi x : A. B \quad \Gamma \vdash a : A}{\Gamma \vdash f \; a : B[a/x]} \text{(T-App)} \\]

## 归纳类型

带有宇宙约束的归纳类型形成：

\\[ \frac{\overline{\Gamma \vdash C_i : A_i \to T \; \text{params}} \quad \Gamma \vdash T : \text{Type}_j}{\Gamma \vdash \text{data } T \text{ where } \overline{C_i : A_i} : \text{Type}_j} \text{(T-Data)} \\]

带有正性约束的构造子类型：

\\[ \frac{\Gamma \vdash I : \text{Type}_i \quad \text{Positive}(I, A)}{\Gamma \vdash c : A \to I} \text{(T-Constr)} \\]

带有依赖消去规则的模式匹配：

\\[ \frac{\begin{array}{c}
\Gamma \vdash t : I \; \overline{p} \\
\Gamma \vdash P : \Pi \overline{x : A}. I \; \overline{x} \to \text{Type}_k \\
\overline{\Gamma \vdash f_i : \Pi \overline{y : B_i}. P \; (c_i \; \overline{y})}
\end{array}}{\Gamma \vdash \text{match } t \text{ return } P \text{ with } \overline{c_i \; \overline{y} \Rightarrow f_i \; \overline{y}} : P \; t} \text{(T-Match)} \\]

## 宇宙多态性

类型中的宇宙变量：

\\[ \frac{\alpha \in \text{UVars}}{\Gamma \vdash \text{Type}\_\alpha : \text{Type}_{\alpha+1}} \text{(T-UVar)} \\]

宇宙层级约束：

\\[ \frac{\Gamma \vdash C\_1 \quad \Gamma \vdash C\_2}{\Gamma \vdash C\_1 \land C_2} \text{(T-Conj)} \\]

\\[ \frac{i \leq j}{\Gamma \vdash i \leq j} \text{(T-Leq)} \\]

宇宙最大值运算：

\\[ \frac{\Gamma \vdash i \leq k \quad \Gamma \vdash j \leq k}{\Gamma \vdash \text{max}(i,j) \leq k} \text{(T-Max)} \\]

## 转换和定义性相等

函数应用的 Beta 归约：

\\[ \frac{}{\Gamma \vdash (\lambda x : A. t) \; s \equiv t[s/x] : B[s/x]} \text{(Conv-Beta)} \\]

函数类型的 Eta 转换：

\\[ \frac{\Gamma \vdash f : \Pi x : A. B \quad x \notin \text{FV}(f)}{\Gamma \vdash f \equiv \lambda x : A. f \; x : \Pi x : A. B} \text{(Conv-Eta)} \\]

模式匹配的 Iota 归约：

\\[ \frac{}{\Gamma \vdash \text{match } (c \; \overline{a}) \text{ return } P \text{ with } \overline{c_i \; \overline{y} \Rightarrow f_i \; \overline{y}} \equiv f \; \overline{a} : P \; (c \; \overline{a})} \text{(Conv-Iota)} \\]

结构转换的相容性规则：

\\[ \frac{\Gamma \vdash s_1 \equiv t_1 : A \to B \quad \Gamma \vdash s_2 \equiv t_2 : A}{\Gamma \vdash s_1 \; s_2 \equiv t_1 \; t_2 : B} \text{(Conv-App)} \\]

## 类型转换和包容性

转换允许将定义性相等的类型互换使用：

\\[ \frac{\Gamma \vdash t : A \quad \Gamma \vdash A \equiv B : \text{Type}_i}{\Gamma \vdash t : B} \text{(T-Conv)} \\]

## 元变量与约束规则

推理的元变量引入：

\\[ \frac{\text{fresh}(\alpha) \quad \Gamma \vdash T : \text{Type}_i}{\Gamma \vdash ?\alpha : T} \text{(T-Meta)} \\]

通过统一求解约束：

\\[ \frac{\Gamma \vdash s : T \quad \Gamma \vdash t : T \quad \text{Unify}(s, t, \sigma)}{\Gamma \vdash s \doteq t : T \leadsto \sigma} \text{(T-Unify)} \\]

通过替换传播约束：

\\[ \frac{\Gamma \vdash C[\sigma] \quad \text{Dom}(\sigma) \subseteq \text{MetaVars}(C)}{\Gamma \vdash C \leadsto \sigma} \text{(T-Subst)} \\]

这些规则捕捉了依赖类型、宇宙约束和元变量统一之间的相互作用，这使得构造演算既具有表现力又难以实现。关键洞察在于，类型检查和约束求解必须协同进行，每个阶段相互告知并约束对方。
