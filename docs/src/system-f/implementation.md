# 实现

好了，现在我们跨越了20世纪70年代那些简单的类型系统，进入80年代更有趣的内容！系统F的双向类型检查代表了一种处理多态类型的方法，无需在每个地方都加上完整的类型标注。双向方法将类型检查分为两种互补模式：**推断**（从表达式中综合出类型）和**检查**（验证表达式是否符合预期的类型）。这种划分使得系统能够优雅地处理类型部分已知或完全未知的情况，在保证类型安全的同时让语言更易用。

## 类型规则

在深入实现细节之前，我们先确立控制系统F的正式类型规则。系好安全带，因为我们即将踏进类型层面魔法王国的奇妙旅程！我们会介绍几个新符号，初次看到可能有点吓人，但一旦熟悉了，它们真的没那么可怕。

* **\\( \Gamma \\) (Gamma)** —— 类型上下文，就像一个字典，将变量映射到它们的类型，并记录我们目前已知的信息。

* **\\( \vdash \\) (Turnstile)** —— “证明”或“蕴含”符号。当我们写 \\( \Gamma \vdash e \Rightarrow A \\) 时，意思是在上下文 \\( \Gamma \\) 下，表达式 \\( e \\) 综合出类型 \\( A \\)。

* **\\( \Rightarrow \\) (双右箭头)** —— 推断模式，用于询问“这个表达式是什么类型？”由类型检查器来回答。

* **\\( \Leftarrow \\) (双左箭头)** —— 检查模式，用于说明“请验证这个表达式具有预期的类型”。我们已知想要的类型是什么。

* **\\( \forall \\) (全称量词)** —— 全称量化，意思是“对所有类型”。看到 \\( \forall \alpha. A \\) 时，它表示“对任意类型 \\( \alpha \\)，我们都有类型 \\( A \\)”。

* **\\( \hat{\alpha} \\) (Hat Alpha)** —— 存在类型变量，类似于类型层面的未知量，由系统在推断过程中求解。可以把它们看作占位符，稍后会被填充。

* **\\( \bullet \\) (实心圆)** —— 应用判断符号，用于我们的推断规则。写 \\( A \bullet e \Rightarrow B \\) 时，意思是“将类型 \\( A \\) 应用于表达式 \\( e \\) 得到类型 \\( B \\)”。

* **\\( <: \\) (子类型)** —— 子类型关系，表示一个类型比另一个类型“更具体”。例如，\\( \text{Int} <: \forall \alpha. \alpha \\) 意味着 Int 是多态类型的子类型。

* **\\( [B/\alpha]A \\)** —— 类型替换，将类型 \\( A \\) 中所有出现的类型变量 \\( \alpha \\) 替换为类型 \\( B \\)。这就是我们实例化多态类型的方式。

现在我们已经装备好了这套符号工具箱，接下来看看这些元素如何组合在一起，构成系统F优雅的类型检查机制。

### 基本规则

变量规则从上下文中查找类型：

\\[ \frac{x : A \in \Gamma}{\Gamma \vdash x \Rightarrow A} \text{(T-Var)} \\]

应用规则检查函数类型是否与参数匹配：

\\[ \frac{\Gamma \vdash e_1 \Rightarrow A \to B \quad \Gamma \vdash e_2 \Leftarrow A}{\Gamma \vdash e_1 \; e_2 \Rightarrow B} \text{(T-App)} \\]

Lambda抽象引入一个新的变量绑定：

\\[ \frac{\Gamma, x : A \vdash e \Leftarrow B}{\Gamma \vdash \lambda x. e \Leftarrow A \to B} \text{(T-Abs)} \\]

### 多态规则

全称引入允许对类型变量进行泛化：

\\[ \frac{\Gamma, \alpha \vdash e \Leftarrow A}{\Gamma \vdash e \Leftarrow \forall \alpha. A} \text{(T-ForallI)} \\]

全称消除实例化多态类型：

\\[ \frac{\Gamma \vdash e \Rightarrow \forall \alpha. A}{\Gamma \vdash e \Rightarrow [B/\alpha]A} \text{(T-ForallE)} \\]

类型标注允许从检查模式切换到推断模式：

\\[ \frac{\Gamma \vdash e \Leftarrow A}{\Gamma \vdash (e : A) \Rightarrow A} \text{(T-Instr)} \\]

### 基本类型规则

整数字面量的类型为 Int：

\\[ \frac{}{\Gamma \vdash n \Rightarrow \text{Int}} \text{(T-LitInt)} \\]

布尔字面量的类型为 Bool：

\\[ \frac{}{\Gamma \vdash \text{true} \Rightarrow \text{Bool}} \text{(T-LitBool)} \\]

### 控制流规则

let绑定引入局部变量：

\\[ \frac{\Gamma \vdash e_1 \Rightarrow A \quad \Gamma, x : A \vdash e_2 \Rightarrow B}{\Gamma \vdash \text{let } x = e_1 \text{ in } e_2 \Rightarrow B} \text{(T-Let)} \\]

条件表达式要求 Bool 类型条件且分支类型一致：

\\[ \frac{\Gamma \vdash e_1 \Leftarrow \text{Bool} \quad \Gamma \vdash e_2 \Rightarrow A \quad \Gamma \vdash e_3 \Leftarrow A}{\Gamma \vdash \text{if } e_1 \text{ then } e_2 \text{ else } e_3 \Rightarrow A} \text{(T-If)} \\]

### 二元操作规则

算术操作接收两个整数并返回一个整数：

\\[ \frac{\Gamma \vdash e_1 \Leftarrow \text{Int} \quad \Gamma \vdash e_2 \Leftarrow \text{Int}}{\Gamma \vdash e_1 \oplus e_2 \Rightarrow \text{Int}} \text{(T-Arith)} \\]

布尔操作接收两个布尔值并返回一个布尔值：

\\[ \frac{\Gamma \vdash e_1 \Leftarrow \text{Bool} \quad \Gamma \vdash e_2 \Leftarrow \text{Bool}}{\Gamma \vdash e_1 \land e_2 \Rightarrow \text{Bool}} \text{(T-Bool)} \\]

比较操作接收两个整数并返回一个布尔值：

\\[ \frac{\Gamma \vdash e_1 \Leftarrow \text{Int} \quad \Gamma \vdash e_2 \Leftarrow \text{Int}}{\Gamma \vdash e_1 < e_2 \Rightarrow \text{Bool}} \text{(T-Cmp)} \\]

相等操作是多态的，适用于任何类型：

\\[ \frac{\Gamma \vdash e_1 \Rightarrow A \quad \Gamma \vdash e_2 \Leftarrow A}{\Gamma \vdash e_1 = e_2 \Rightarrow \text{Bool}} \text{(T-Eq)} \\]

### 双向规则

模式切换允许将推断结果用于检查：

\\[ \frac{\Gamma \vdash e \Rightarrow A}{\Gamma \vdash e \Leftarrow A} \text{(T-Sub)} \\]

存在变量用于未知类型：

\\[ \frac{\Gamma, \hat{\alpha} \vdash e \Rightarrow A}{\Gamma \vdash e \Rightarrow [\hat{\alpha}/\alpha]A} \text{(T-InstL)} \\]

### 应用推断规则

应用推断处理函数类型未立即知晓的复杂情况：

带箭头类型的应用：
\\[ \frac{\Gamma \vdash e_2 \Leftarrow A}{\Gamma \vdash A \to B \bullet e_2 \Rightarrow B} \text{(T-AppArrow)} \\]

带存在变量的应用：
\\[ \frac{\Gamma[\hat{\alpha} := \hat{\alpha_1} \to \hat{\alpha_2}], \hat{\alpha_1}, \hat{\alpha_2} \vdash e_2 \Leftarrow \hat{\alpha_1}}{\Gamma \vdash \hat{\alpha} \bullet e_2 \Rightarrow \hat{\alpha_2}} \text{(T-AppEVar)} \\]

在这些规则中，\\( \Rightarrow \\) 表示**推断**模式（综合出类型），而 \\( \Leftarrow \\) 表示**检查**模式（对照预期类型进行验证）。帽子符号 \\( \hat{\alpha} \\) 表示存在类型变量，系统会在推断过程中求解它们。

## 核心数据结构

### 上下文与环境管理

双向算法维护一个上下文，该上下文跟踪多种类型的绑定和约束。我们的上下文系统不仅需要处理项变量及其类型，还需要处理类型变量、存在变量以及它们之间的关系。

```rust
#![enum!("system-f/src/typecheck.rs", Entry)]
```

上下文条目代表类型检查器在整个双向推理过程中需要跟踪的不同种类的信息。变量绑定表示为 `VarBnd(TmVar, Type)`，将项变量与其类型关联起来，例如记录当前作用域中 `x` 具有类型 `Int`。类型变量绑定表示为 `TVarBnd(TyVar)`，将类型变量引入作用域，例如出现在全称量化 \\( \forall \alpha. \ldots \\) 中的 \\( \alpha \\)。

存在类型变量绑定写作 `ETVarBnd(TyVar)`，引入表示待通过约束求解确定未知类型的类型变量。已求解的存在类型变量绑定表示为 `SETVarBnd(TyVar, Type)`，记录推理过程中为存在变量发现的具体解。最后，标记条目表示为 `Mark(TyVar)`，标记作用域的开始，以便在退出作用域时正确垃圾回收类型变量。

上下文本身以类似栈的结构维护这些条目，其中顺序对于作用域和变量解析至关重要：

```rust
#![struct!("system-f/src/typecheck.rs", Context)]
```

上下文管理需要仔细关注作用域规则。当我们进入多态函数或引入新类型变量时，必须确保在退出其作用域时正确清理它们。上下文提供了拆分和重构的方法，以高效处理这些操作。

### 类型替换与应用

类型替换构成了我们 System F 实现的计算核心。当实例化多态类型或求解存在变量时，我们需要在复杂类型表达式中系统地将类型变量替换为具体类型。

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::subst_type)]
```

替换必须正确处理变量捕获。当替换到 `Forall` 类型时，我们必须确保绑定变量不与替换类型冲突。这类似于 lambda 演算中的 alpha-转换，但在类型层面操作。

上下文应用通过将存在变量解的当前状态应用到类型来扩展替换：

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::apply_ctx_type)]
```

此操作至关重要，因为我们的算法逐步构建存在变量的解。随着我们对未知类型的了解更多，我们需要通过所有正在处理的类型传播此信息。

## 双向算法核心

### 推理规则

推理模式从表达式综合类型。我们的实现采用模块化方法，主推理函数将每种语法形式委托给专门的方法。

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer)]
```

推理函数委托给实现各个类型规则的方法：

**变量查找** 遵循 T-Var 规则：

\\[ \frac{x : A \in \Gamma}{\Gamma \vdash x \Rightarrow A} \text{(T-Var)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_var)]
```

**整数字面量** 使用 T-LitInt 规则：

\\[ \frac{}{\Gamma \vdash n \Rightarrow \text{Int}} \text{(T-LitInt)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_lit_int)]
```

**布尔字面量** 使用 T-LitBool 规则：

\\[ \frac{}{\Gamma \vdash \text{true} \Rightarrow \text{Bool}} \text{(T-LitBool)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_lit_bool)]
```

**Lambda 抽象** 实现 T-Abs 规则：

\\[ \frac{\Gamma, x : A \vdash e \Leftarrow B}{\Gamma \vdash \lambda x. e \Leftarrow A \to B} \text{(T-Abs)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_abs)]
```

**函数应用** 使用 T-App 规则：

\\[ \frac{\Gamma \vdash e_1 \Rightarrow A \to B \quad \Gamma \vdash e_2 \Leftarrow A}{\Gamma \vdash e_1 \; e_2 \Rightarrow B} \text{(T-App)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_application)]
```

**Let 绑定** 实现 T-Let 规则：

\\[ \frac{\Gamma \vdash e_1 \Rightarrow A \quad \Gamma, x : A \vdash e_2 \Rightarrow B}{\Gamma \vdash \text{let } x = e_1 \text{ in } e_2 \Rightarrow B} \text{(T-Let)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_let)]
```

**条件表达式** 使用 T-If 规则：

\\[ \frac{\Gamma \vdash e_1 \Leftarrow \text{Bool} \quad \Gamma \vdash e_2 \Rightarrow A \quad \Gamma \vdash e_3 \Leftarrow A}{\Gamma \vdash \text{if } e_1 \text{ then } e_2 \text{ else } e_3 \Rightarrow A} \text{(T-If)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_if)]
```

**二元运算** 实现 T-BinOp 规则（T-Arith、T-Bool、T-Cmp、T-Eq）：

\\[ \frac{\Gamma \vdash e_1 \Leftarrow \text{Int} \quad \Gamma \vdash e_2 \Leftarrow \text{Int}}{\Gamma \vdash e_1 \oplus e_2 \Rightarrow \text{Int}} \text{(T-Arith)} \\]

\\[ \frac{\Gamma \vdash e_1 \Leftarrow \text{Bool} \quad \Gamma \vdash e_2 \Leftarrow \text{Bool}}{\Gamma \vdash e_1 \land e_2 \Rightarrow \text{Bool}} \text{(T-Bool)} \\]

\\[ \frac{\Gamma \vdash e_1 \Leftarrow \text{Int} \quad \Gamma \vdash e_2 \Leftarrow \text{Int}}{\Gamma \vdash e_1 < e_2 \Rightarrow \text{Bool}} \text{(T-Cmp)} \\]

\\[ \frac{\Gamma \vdash e_1 \Rightarrow A \quad \Gamma \vdash e_2 \Leftarrow A}{\Gamma \vdash e_1 = e_2 \Rightarrow \text{Bool}} \text{(T-Eq)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_binop)]
```

**类型注解** 使用 T-Instr 规则：

\\[ \frac{\Gamma \vdash e \Leftarrow A}{\Gamma \vdash (e : A) \Rightarrow A} \text{(T-Instr)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_ann)]
```

**类型抽象** 实现 T-TAbs 规则：

\\[ \frac{\Gamma, \alpha \vdash e \Rightarrow A}{\Gamma \vdash \Lambda \alpha. e \Rightarrow \forall \alpha. A} \text{(T-TAbs)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_tabs)]
```

**类型应用** 使用 T-TApp 规则：

\\[ \frac{\Gamma \vdash e \Rightarrow \forall \alpha. A}{\Gamma \vdash e[B] \Rightarrow [B/\alpha]A} \text{(T-TApp)} \\]

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_tapp)]
```

每个方法都包含将其链接到所实现的形式类型规则的注释，使理论与实现之间的对应关系明确。

### 检查规则

检查模式验证表达式是否符合预期的类型。通过这种方式，算法即使在类型尚未完全确定的情况下也能取得进展。

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::check)]
```

检查模式提供了专门的推理方式，利用已知的类型信息更高效地引导推理过程。对于 lambda 表达式，当将 \\( \\lambda x:\\tau_1. e \\) 与类型 \\( \\tau_1 \\to \\tau_2 \\) 进行核对时，算法可以立即验证参数类型是否匹配，然后递归地将表达式体 \\( e \\) 与预期返回类型 \\( \\tau_2 \\) 进行核对。这种直接分解避免了先综合类型再验证兼容性的步骤。

当将表达式与全称类型 \\( \\forall\\alpha. \\tau \\) 进行核实时，算法会将类型变量 \\( \\alpha \\) 引入到上下文中，然后将表达式与实例化后的类型 \\( \\tau \\) 进行核对。这种方法确保正确处理全称量化，同时保持合理类型检查所需的域限制规则。当当前的表达式与预期类型的组合不适用直接检查策略时，算法会回退到综合加子类型的方法：首先综合出表达式的类型，然后验证该综合类型是否为预期类型的子类型。

## 子类型与实例化

### 子类型关系

System F 包含一个子类型系统，用于处理多态类型之间的关系。其核心思想在于 `∀α. τ` 比任何 `τ` 的具体实例化都更通用。

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::subtype)]
```

子类型规则捕获了在 System F 中支配类型兼容性的几个关键关系。函数类型表现出经典的逆变-协变模式：接受更一般参数并返回更具体结果的函数，被视为接受更具体参数并返回更一般结果的函数的子类型。这意味着类型 \\( A_1 \\to B_1 \\) 是 \\( A_2 \\to B_2 \\) 的子类型，当且仅当 \\( A_2 \\leq A_1 \\)（参数逆变）且 \\( B_1 \\leq B_2 \\)（结果协变）。

全称量化遵循的原则是：\\( \\forall\\alpha. \\tau_1 \\leq \\tau_2 \\) 成立，当且仅当在将 \\( \\alpha \\) 实例化为一个全新的存在变量后 \\( \\tau_1 \\leq \\tau_2 \\) 成立。这实际上允许通过多态类型的实例化来关联它们。当子类型涉及存在变量时，算法必须解决关于这些变量应如何实例化才能满足子类型关系的约束，这通常会生成额外的约束并在系统中传播。

### 变量实例化

实例化判定处理了多态类型检查中的核心复杂性。当我们遇到诸如 `^α ≤ τ`（存在变量应最多与某个类型一样通用）这样的约束时，需要找到适当的实例化。

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::inst_l)]
```

左实例化（`inst_l`）处理存在变量在约束左侧的情况。这通常意味着我们在寻找满足该约束的最一般类型。

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::inst_r)]
```

右实例化（`inst_r`）处理存在变量在右侧的互补情况。这通常意味着我们在寻找满足该约束的最具体类型。

实例化算法仔细处理了约束求解过程中出现的若干复杂情形。当两个存在变量相互约束时出现“可达”关系，要求算法决定哪个变量应基于另一个变量进行求解，同时保持适当的顺序约束。箭头类型实例化需要将函数类型分解为其参数和返回值类型，并为每个分量创建独立的实例化约束，这些约束必须一致地求解。

实例化与全称量化之间的交互带来了特殊的挑战，因为算法必须确保多态类型被正确实例化，同时保持域限制规则，防止类型变量逃逸出其预期作用域。这些情况需要精细的约束管理，以确保在求解过程中维护所有关系。

### 出现检查

健全类型推断的一个关键组成部分是发生检查（occurs check），它可以防止在合一过程中产生无限类型。在求解诸如 `^α := τ` 这样的约束时，我们必须确保 `α` 不在 `τ` 中出现，否则会形成循环类型。

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::occurs_check)]
```

发生检查在实例化的 InstLSolve 和 InstRSolve 情形中应用。没有这个检查，类型系统可能会接受导致无限类型的程序，从而破坏类型检查的可判定性。

### 应用推断

System F 中的函数应用需要仔细处理，因为函数类型可能并非显而易见。`infer_app` 判定实现了前面定义的 T-AppArrow 和 T-AppEVar 规则：

```rust
#![function!("system-f/src/typecheck.rs", BiDirectional::infer_app)]
```

该实现通过不同的推理规则处理两个核心的应用场景。T-AppArrow 规则适用于函数具有已知箭头类型 \\( A \\to B \\) 的情况，允许算法将参数与 \\( A \\) 进行核对，并返回 \\( B \\) 作为结果类型。这个简单的情形对应于实现中的 `Type::Arrow` 模式，代表了标准的函数应用场景。

T-AppEVar 规则处理函数类型为存在变量 \\( \\hat{\\alpha} \\) 的更复杂情况。在这种情况下，算法将存在变量实例化为 \\( \\hat{\\alpha_1} \\to \\hat{\\alpha_2} \\)，其中包含全新的存在变量，然后将参数与 \\( \\hat{\\alpha_1} \\) 进行核对，并返回 \\( \\hat{\\alpha_2} \\) 作为结果类型。这对应于 `Type::ETVar` 情形，使得即使函数类型最初未知时也能进行类型推断。

当函数具有多态的 `Forall` 类型时，实例化通过子类型机制（使用 SubAllL 规则）来处理，而不是直接在应用推断中处理。这种设计选择确保了健全性，将多态实例化路由到已建立好的子类型基础设施中，并遵循标准的双向算法设计模式。

## 错误处理

我们的实现提供了全面的错误报告，能区分解析错误和类型错误。解析错误使用基于源位置的 ariadne 报告，而类型错误则提供被推断表达式及其类型的上下文信息。

```rust
#![enum!("system-f/src/errors.rs", TypeError)]
```

类型错误系统包含了表达式上下文，帮助开发者理解类型检查过程中失败的位置。每个错误变体都包含一个 `expr` 字段，存储着错误发生时正在被推断类型的表达式，这为调试提供了宝贵信息。

解析错误得到了增强处理，带有源位置信息以实现精确的错误报告：

```rust
#![enum!("system-f/src/errors.rs", ParseError)]
```

这种双管齐下的方法确保语法错误能够获得精确的源位置反馈，而类型错误则聚焦于表达式与类型之间的逻辑关系。

## 端到端验证

为了展示完整的 System F 实现，以及所有模块化类型规则如何协同工作，考虑以下对整数参数进行加倍的 lambda 表达式：

```bash
$ cargo run -- check "\x : Int -> x + x"
```

系统会输出以下完整的推导过程：

```
Parsed expression: Abs("x", Int, BinOp(Add, Var("x"), Var("x")))

Type checking successful!
Final type: Int -> Int

InfLam:  ⊢ Abs("x", Int, BinOp(Add, Var("x"), Var("x"))) =>  ⊢ Abs("x", Int, BinOp(Add, Var("x"), Var("x"))) ⇒ Int -> ^α0 ⊣ ^α0 = Int
  ChkSub: ^α0, x: Int ⊢ BinOp(Add, Var("x"), Var("x")) ⇐ ^α0 => ^α0 = Int, x: Int
    InfArith: ^α0, x: Int ⊢ BinOp(Add, Var("x"), Var("x")) => ^α0, x: Int ⊢ BinOp(Add, Var("x"), Var("x")) ⇒ Int ⊣ ^α0, x: Int
      ChkSub: ^α0, x: Int ⊢ Var("x") ⇐ Int => ^α0, x: Int
        InfVar: ^α0, x: Int ⊢ Var("x") => ^α0, x: Int ⊢ Var("x") ⇒ Int ⊣ ^α0, x: Int
        SubRefl: ^α0, x: Int ⊢ Int <: Int => ^α0, x: Int
      ChkSub: ^α0, x: Int ⊢ Var("x") ⇐ Int => ^α0, x: Int
        InfVar: ^α0, x: Int ⊢ Var("x") => ^α0, x: Int ⊢ Var("x") ⇒ Int ⊣ ^α0, x: Int
        SubRefl: ^α0, x: Int ⊢ Int <: Int => ^α0, x: Int
    SubInstR: ^α0, x: Int ⊢ Int <: ^α0 => ^α0 = Int, x: Int
      InstRSolve: ^α0, x: Int ⊢ Int :=< ^α0 => ^α0 = Int, x: Int
```

最终结果显示 `Final type: Int -> Int`，正确推断出该 lambda 表达式是一个从整数到整数的函数！证明树中的存在变量 `^α0` 通过约束求解过程被解析为 `Int`，而最终的类型应用确保了所有存在变量均在输出中得到恰当替换。

对于非平凡表达式，约束求解过程可能涉及更复杂的推理，并需要额外的推导步骤；但借助证明树方法，我们可以可视化推导步骤并理解被求解的约束。这是一种非常强大的技术。

## 任务完成

好了，就这样！一个完整的双向类型检查器，支持 System F 的多态类型、存在变量和约束求解！该算法处理了综合模式与检查模式之间复杂的交互，以生产级类型系统所需的精度管理存在变量和子类型关系。

双向方法将一个原本可能令人望而却步的推导问题转化为一个系统化、可判定的过程，既提供了强大的表达能力，又保证了可靠的类型安全性。System F 的多态性开启了一个全新的类型安全编程世界，一旦你亲眼目睹它的运作，简直就像魔法一样！
