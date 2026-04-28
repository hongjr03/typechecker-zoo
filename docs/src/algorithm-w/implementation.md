# 核心实现

算法 W 是函数式编程语言中类型推断问题最早且最优雅（在当时）的解决方案之一。由 Robin Milner 于 1978 年提出，它为 [Hindley-Milner 类型系统](https://en.wikipedia.org/wiki/Hindley%E2%80%93Milner_type_system) 中推断最通用类型提供了一种可靠且完备的方法。本节探讨我们的 Rust 实现，考察数学基础如何转化为能够处理 lambda 抽象、函数应用、let 多态性和复杂合一场景的实用代码。

算法 W 的核心洞见在于它通过约束生成和合一来系统地进行类型推断。该算法并不试图通过局部分析来确定类型，而是生成类型变量、收集约束，然后通过合一求解这些约束，从而构建全局图像。这种方法确保我们始终能找出最通用的类型，这一特性对于支持函数式语言中的多态性至关重要。

你经常会看到这个算法（或令人困惑地，类型系统）被冠以多个名称：

*   **Hindley-Milner**
*   **Hindley-Damas-Milner**
*   **Damas-Milner**
*   **HM**
*   **算法 W**

## 类型规则

在深入实现细节之前，我们先确立支配 Hindley-Milner 类型系统的形式化类型规则。我们将介绍一些捕捉类型推断本质的数学符号，但别担心，一旦深入了解细节，每个符号都会有精确而直观的含义。

*   **\\( \tau \\) (Tau)** – 表示单态类型，例如 \\( \text{Int} \\)、\\( \text{Bool} \\) 或 \\( \text{Int} \to \text{Bool} \\)。这些是具体的、完全确定的类型。
*   **\\( \alpha, \beta, \gamma \\) (希腊字母)** – 类型变量，在推断期间代表未知类型。可以把它们看作在求解过程中被确定的类型层面的未知量。
*   **\\( \Gamma \\) (Gamma)** – 类型环境，将变量映射到它们的类型。它就像一个字典，记录着我们对每个变量类型的已知信息。
*   **\\( \vdash \\) (Turnstile)** – “导出”或“证明”符号。当我们写 \\( \Gamma \vdash e : \tau \\) 时，意思是“在环境 \\( \Gamma \\) 中，表达式 \\( e \\) 具有类型 \\( \tau \\)”。
*   **\\( \sigma \\) (Sigma)** – 表示多态类型方案，例如 \\( \forall \alpha. \alpha \to \alpha \\)。这些方案可以用不同的具体类型进行实例化。
*   **\\( \forall \alpha \\) (Forall Alpha)** – 对类型变量的全称量化。意思是“对于任意类型 \\( \alpha \\)”。这是我们表达多态性的方式。
*   **\\( [\tau/\alpha]\sigma \\)** – 类型替换，将方案 \\( \sigma \\) 中所有出现的类型变量 \\( \alpha \\) 替换为类型 \\( \tau \\)。这是我们实例化多态类型的方式。
*   **\\( S \\) (Substitution)** – 从类型变量到类型的映射，代表通过合一找到的解。
*   **\\( \text{gen}(\Gamma, \tau) \\)** – 泛化，通过对环境中不存在的类型变量进行量化，将单类型转换为多类型。
*   **\\( \text{inst}(\sigma) \\)** – 实例化，通过用量化的变量替换为新的类型变量，从多类型创建一个新的单类型。
*   **\\( \text{ftv}(\tau) \\)** – 自由类型变量，出现在类型 \\( \tau \\) 中未绑定的类型变量集合。
*   **\\( \emptyset \\) (空集)** – 空替换，表示对类型不做任何改动。
*   **\\( [\alpha \mapsto \tau] \\)** – 一个替换，将类型变量 \\( \alpha \\) 映射到类型 \\( \tau \\)。
*   **\\( S_1 \circ S_2 \\)** – 替换的组合，先应用 \\( S_2 \\)，再应用 \\( S_1 \\)。
*   **\\( \notin \\) (不包含)** – 集合成员关系的否定，用于发生检查中防止无限类型。

### 类型规则

变量规则从环境中查找类型：
\\[ \\frac{x : σ \\in Γ \\quad τ = \\text{inst}(σ)}{Γ ⊢ x : τ} \\text{(T-Var)} \\]

Lambda 抽象引入新的变量绑定：
\\[ \\frac{Γ, x : α ⊢ e : τ \\quad α \\text{ fresh}}{Γ ⊢ λx. e : α → τ} \\text{(T-Lam)} \\]

函数应用通过合一组合类型：
\\[ \\frac{Γ ⊢ e₁ : τ₁ \\quad Γ ⊢ e₂ : τ₂ \\quad α \\text{ fresh} \\quad S = \\text{unify}(τ₁, τ₂ → α)}{Γ ⊢ e₁ \\, e₂ : S(α)} \\text{(T-App)} \\]

Let 多态性允许泛化：
\\[ \\frac{Γ ⊢ e₁ : τ₁ \\quad σ = \\text{gen}(Γ, τ₁) \\quad Γ, x : σ ⊢ e₂ : τ₂}{Γ ⊢ \\text{let } x = e₁ \\text{ in } e₂ : τ₂} \\text{(T-Let)} \\]

字面量有它们对应的基础类型：
\\[ \\frac{}{Γ ⊢ n : \\text{Int}} \\text{(T-LitInt)} \\]

\\[ \\frac{}{Γ ⊢ b : \\text{Bool}} \\text{(T-LitBool)} \\]

这些规则捕捉了 Hindley-Milner 类型系统的本质。如果觉得信息量太大，别担心！直接跳到 Rust 代码部分，试着将公式中的符号与实际代码行对应起来，很快你就会发现它们是如何与代码对应的。它们之间存在一一映射关系，虽然符号看起来复杂，但在代码中实际上是直截了当的表达式，大多只是操作、查找和合并哈希表。

## 抽象语法树

我们的实现始于将表达式和类型都精心建模为代数数据类型。表达式语言在保持理论基础的同时，用实用的构造扩展了纯 lambda 演算。

```rust
#![enum!("algorithm-w/src/ast.rs", Expr)]
```

表达式 AST 捕捉了我们语言的基本构造。变量 (`Var`) 和函数抽象 (`Abs`) 直接对应 lambda 演算。函数应用 (`App`) 通过 beta 归约驱动计算。`Let` 构造引入局部绑定，并具有多态泛化的潜力，而字面量 (`Lit`) 和元组 (`Tuple`) 则提供了具体的数据类型，使语言能够胜任实际的编程任务。

类型系统通过自己的 AST 反映了这种结构，该 AST 代表了这些表达式可以拥有的类型。

```rust
#![enum!("algorithm-w/src/ast.rs", Type)]
```

类型变量 (`Type::Var`) 在推断中充当占位符，最终通过合一被实例化为具体类型。箭头类型 (`Type::Arrow`) 表示函数类型，编码了参数和返回类型。像 `Int` 和 `Bool` 这样的基础类型提供了基础，而元组类型 (`Type::Tuple`) 则支持结构化数据。这些类型的递归性质使我们能够表达任意复杂的类型结构，从简单的整数到高阶函数（操作其他函数）都涵盖在内。

## 类型推断算法

算法 W 基于几个捕捉类型推断核心概念的基本数据结构运行。这些类型别名为核心抽象提供了名称，使算法的实现更易读。

类型变量抽象表示那些将在推断过程中被求解的未知类型。项变量代表出现在表达式中的程序变量。类型环境将项变量映射到它们的类型，而替换则将类型变量映射到具体类型。

```rust
pub type TyVar = String;
pub type TmVar = String;
pub type Env = BTreeMap<TmVar, Scheme>;  // 现在存储的是类型方案，而非类型
pub type Subst = HashMap<TyVar, Type>;
```

这些类型别名封装了算法 W 中的基本数据流。类型变量如 `t0`、`t1` 和 `t2` 作为占位符，随着推断的进行与具体类型进行合一。项变量代表源程序中的实际标识符。环境现在追踪的是多态类型方案，而不仅是类型，从而支持正确的 let 多态性，而替换则记录了通过合一发现的解。

选择 `String` 作为类型变量和项变量的类型，反映了我们实现的简洁性。在完整的实现中，系统通常会使用更复杂的表示，例如类型变量的 de Bruijn 索引或字符串驻留以提升性能，但使用字符串有助于理解基本算法。

我们算法 W 实现的核心在于 `TypeInference` 结构体，它维护了对整个程序进行可靠类型推断所需的状态。

```rust
#![struct!("algorithm-w/src/infer.rs", TypeInference)]
```

推断引擎的主要职责是生成新的类型变量，这一过程确保每个未知类型获得唯一的标识符。这种基于计数的方法提供了一种简单而有效的方式来避免推断过程中命名冲突。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::fresh_tyvar)]
```

新鲜变量生成构成了算法 W 系统化处理未知类型的基础。每当我们遇到一个类型未知的表达式时，就为其分配一个新鲜的类型变量。随着对程序结构了解的深入，这些变量随后会与具体类型进行合一。

## 替换与合一

类型替换是算法 W 的核心计算机制。替换将类型变量映射到具体类型，实际上“求解”了类型推断谜题的一部分。

替换的应用必须正确处理类型的递归结构，确保替换能传播到复合类型（如箭头类型和元组类型）中。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::apply_subst)]
```

替换应用展示了类型信息如何在系统中流动。当我们将替换应用于箭头类型时，必须递归地将其应用于参数类型和返回类型。这确保了在程序某一部分发现的类型信息能正确影响其他部分。

替换的组合允许我们将多个部分解合并为对程序类型的更完整理解。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::compose_subst)]
```

组合操作确保当我们在推断过程的不同部分得到多个替换时，能够将它们合并成一个单一的、一致的替换，该替换代表了我们对程序类型的累积知识。

当发现新的类型信息时，替换还必须应用于整个类型环境。此操作根据当前替换更新环境中的所有类型。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::apply_subst_env)]
```

环境替换对于在推断过程中保持一致性至关重要。当我们发现某个类型变量应该被实例化为具体类型时，不仅需要更新单个类型，还需要更新整个类型环境以反映这一新知识。

### 合一

合一是类型推断的核心，用于求解类型之间的约束。合一算法生成使两个类型等价的替换：

自反性——相同的类型平凡地合一：
\\[ \\frac{}{\\text{unify}(τ, τ) = \\emptyset} \\text{(U-Refl)} \\]

带出现检查的变量合一：
\\[ \\frac{α \\notin \\text{ftv}(τ)}{\\text{unify}(α, τ) = [α ↦ τ]} \\text{(U-VarL)} \\]

\\[ \\frac{α \\notin \\text{ftv}(τ)}{\\text{unify}(τ, α) = [α ↦ τ]} \\text{(U-VarR)} \\]

箭头类型合一分解为定义域和值域：
\\[ \\frac{S₁ = \\text{unify}(τ₁, τ₃) \\quad S₂ = \\text{unify}(S₁(τ₂), S₁(τ₄))}{\\text{unify}(τ₁ → τ₂, τ₃ → τ₄) = S₂ ∘ S₁} \\text{(U-Arrow)} \\]

元组合一需要分量逐个合一：
\\[ \\frac{S₁ = \\text{unify}(τ₁, τ₃) \\quad S₂ = \\text{unify}(S₁(τ₂), S₁(τ₄))}{\\text{unify}((τ₁, τ₂), (τ₃, τ₄)) = S₂ ∘ S₁} \\text{(U-Tuple)} \\]

基本类型合一仅在类型相同时成功：
\\[ \\frac{}{\\text{unify}(\\text{Int}, \\text{Int}) = \\emptyset} \\text{(U-Int)} \\]

\\[ \\frac{}{\\text{unify}(\\text{Bool}, \\text{Bool}) = \\emptyset} \\text{(U-Bool)} \\]

这些合一规则确保类型约束被系统地求解，同时通过出现检查维持可靠性。

当我们有两个必须相等的类型（例如函数的参数类型和传递给它的实参类型）时，合一会判断该约束是否可满足，如果可以，则找出使它们相等的替换。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::unify)]
```

合一算法处理几种不同的情况，每种情况对应不同的约束求解场景。当两个相同的基类型（如 `Int` 与 `Int`）合一时，不需要任何替换。当将一个类型变量与任何其他类型合一时，我们创建一个将该变量映射到那个类型的替换，前提是出现检查通过。

出现检查通过确保类型变量不出现于正在与之合一的类型内部，从而防止无限类型。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::occurs_check)]
```

此检查对于可靠性至关重要。没有它，我们可能生成像 `t0 = t0 -> Int` 这样的无限类型，这会破坏类型系统的可判定性。

对于复合类型（如箭头类型），合一天然是递归的。我们必须合一对应的子组件，然后组合所得的替换。这一过程确保复杂类型保持其结构关系，同时允许类型变量的灵活实例化。

## 主推断算法

中心的 `infer` 方法实现了算法 W 本身，分析表达式以确定其类型，同时累加必要的替换。我们的实现采用模块化方式，每个语法结构都有其自己的辅助方法，实现相应的类型规则。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::infer)]
```

每个辅助方法都直接对应一个形式化类型规则，使得理论与实现之间的关系清晰可见。

### 变量查找

\\[ \\frac{x : σ \\in Γ \\quad τ = \\text{inst}(σ)}{Γ ⊢ x : τ} \\text{(T-Var)} \\]

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::infer_var)]
```

变量查找需要实例化多态类型。当我们在环境中找到变量时，它可能具有像 `∀α. α → α` 这样的多态类型方案。我们通过用量化的类型变量替换为新鲜的类型变量来创建一个新的单态实例。

### Lambda 抽象

\\[ \\frac{Γ, x : α ⊢ e : τ \\quad α \\text{ fresh}}{Γ ⊢ λx. e : α → τ} \\text{(T-Lam)} \\]

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::infer_abs)]
```

Lambda 抽象引入了新的变量绑定。我们为参数分配一个新鲜的类型变量，扩展环境，然后推断函数体的类型。在函数体推断过程中发现的任何约束都会通过替换传播回来。

### 函数应用

\\[ \\frac{Γ ⊢ e₁ : τ₁ \\quad Γ ⊢ e₂ : τ₂ \\quad α \\text{ fresh} \\quad S = \\text{unify}(τ₁, τ₂ → α)}{Γ ⊢ e₁ \\, e₂ : S(α)} \\text{(T-App)} \\]

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::infer_app)]
```

应用驱动了约束生成。我们为函数和参数分别推断类型，然后将函数类型与一个由参数类型和新鲜结果类型变量构建的箭头类型进行合一。

### Let 多态性

\\[ \\frac{Γ ⊢ e₁ : τ₁ \\quad σ = \\text{gen}(Γ, τ₁) \\quad Γ, x : σ ⊢ e₂ : τ₂}{Γ ⊢ \\text{let } x = e₁ \\text{ in } e₂ : τ₂} \\text{(T-Let)} \\]

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::infer_let)]
```

Let 表达式通过泛化实现了多态性。在推断出绑定表达式的类型后，我们通过对未被环境约束的类型变量进行量化来泛化它。这允许在 let 体内进行多态使用。

### 字面量类型

\\[ \\frac{}{Γ ⊢ n : \\text{Int}} \\text{(T-LitInt)} \\]

\\[ \\frac{}{Γ ⊢ b : \\text{Bool}} \\text{(T-LitBool)} \\]

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::infer_lit_int)]
```

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::infer_lit_bool)]
```

字面量具有已知类型，无需生成约束。

## 泛化与实例化

泛化和实例化机制处理 let 多态性，允许在 let 表达式中绑定的变量以多种不同类型被使用。

### 通过示例理解泛化

泛化将具体类型转换为多态类型方案。考虑这个简单的例子：

```haskell
let id = \x -> x in (id 42, id true)
```

当我们推断 `\x -> x` 的类型时，会得到类似 `t0 → t0` 的结果，其中 `t0` 是一个类型变量。由于 `t0` 没有在其他任何地方出现，我们可以将其泛化为 `∀t0. t0 → t0`，使 `id` 成为多态的。

这就是允许 `id` 在同一表达式中同时与 `42`（类型 `Int`）和 `true`（类型 `Bool`）一起使用的原因。如果没有泛化，第一次使用会将 `t0` 固定为 `Int`，导致第二次使用失败。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::generalize)]
```

泛化通过检查哪些类型变量没有在当前环境中自由出现，来识别可以变为多态的类型变量。如果一个类型变量没有被作用域中的任何其他东西约束，那么对它进行量化是安全的。

### 通过示例理解实例化

实例化从多态类型创建新的单态版本。当我们使用像恒等函数这样的多态函数时，我们需要为每次使用创建其类型的新副本。

考虑这个表达式：

```haskell
let id = \x -> x in id id
```

这里我们将多态恒等函数应用于自身。第一个 `id` 被实例化为 `(α → α) → (α → α)`，而第二个 `id` 被实例化为 `α → α`。这些不同的实例化使得应用能够成功进行类型检查。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::instantiate)]
```

实例化将量化的类型变量替换为新鲜的类型变量。这确保了多态函数的每次使用都有自己独立的类型约束，防止不同调用点之间的干扰。

### 自由类型变量

泛化依赖于计算单个类型和整个环境中的自由类型变量。这些操作识别哪些类型变量可能被泛化，哪些已经被约束。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::free_type_vars)]
```

自由类型变量的计算递归遍历类型结构，收集所有未绑定出现的类型变量。对于复合类型如箭头和元组，它必须遍历所有子组件以确保没有遗漏变量。

```rust
#![function!("algorithm-w/src/infer.rs", TypeInference::free_type_vars_env)]
```

计算整个环境中的自由变量需要检查环境中的每个类型，并取其自由变量的并集。这给出了当前上下文约束的完整类型变量集合。

我们的完整实现通过为方案中每个量化变量在实例化时生成新鲜类型变量来完全支持多态实例化。这一机制使得恒等函数能够在一个上下文中作用于整数，在另一个上下文中作用于布尔值，正如 `let id = \x -> x in (id, id)` 这样的表达式所示，它会产生类型 `(t1 -> t1, t2 -> t2)`，展示了正确的多态实例化。

## 错误处理与推理树

我们的实现提供了详细的错误报告，并生成了推理树，展示了逐步推理的过程。

```rust
#![struct!("algorithm-w/src/infer.rs", InferenceTree)]
```

这些推理树既用于调试也用于教学目的。它们显式地展示了算法 W 所执行的隐式推理，说明了类型信息如何在程序中流动，以及约束如何被生成和求解。

公共接口提供了生成树和仅类型两种推理版本，支持从交互式开发到自动化工具的不同使用场景。

```rust
#![function!("algorithm-w/src/infer.rs", infer_type_only)]
```

## 使用示例

为了看算法 W 的实际效果，让我们对一个展示 let 多态性和泛化的多态函数进行类型检查：

```bash
$ cargo run -- "let const = \\x -> \\y -> x in const 42 true"
```

这会输出以下清晰的输出，展示了完整的推理过程：

```
Parsed expression: let const = λx.λy.x in const 42 true

Type inference successful!
Final type: Int
```

推理追踪：
T-Let: {} ⊢ let const = λx.λy.x in const 42 true ⇒ => Int
  T-Abs: {} ⊢ λx.λy.x ⇒ => t0 → t1 → t0
    T-Abs: {x: t0} ⊢ λy.x ⇒ => t1 → t0
      T-Var: {x: t0, y: t1} ⊢ x ⇒ => t0
  T-App: {const: forall t0 t1. t0 → t1 → t0} ⊢ const 42 true ⇒ => Int
    T-App: {const: forall t0 t1. t0 → t1 → t0} ⊢ const 42 ⇒ => t5 → Int
      T-Var: {const: forall t0 t1. t0 → t1 → t0} ⊢ const ⇒ => t4 → t5 → t4
      T-Int: {const: forall t0 t1. t0 → t1 → t0} ⊢ 42 ⇒ => Int
      Unify-Arrow: t4 → t5 → t4 ~ Int → t3 => {t5 → Int/t3, Int/t4}
        Unify-Var: t4 ~ Int => {Int/t4}
        Unify-Var: t5 → Int ~ t3 => {t5 → Int/t3}
    T-Bool: {const: forall t0 t1. t0 → t1 → t0} ⊢ true ⇒ => Bool
    Unify-Arrow: t5 → Int ~ Bool → t2 => {Int/t2, Bool/t5}
      Unify-Var: t5 ~ Bool => {Bool/t5}
      Unify-Var: Int ~ t2 => {Int/t2}
```

该追踪展示了算法 W 的几个关键方面：

1. **泛化**：lambda 表达式 `\x -> \y -> x` 初始获得类型 `t0 → t1 → t0`，但当它在 let 表达式中绑定到 `const` 时，被泛化为 `∀t0 t1. t0 → t1 → t0`。

2. **实例化**：当 `const` 在应用中使用时，它会被实例化为新的类型变量 `t4` 和 `t5`，从而允许其多态使用。

3. **合一**：将 `const` 应用于 `42` 和 `true` 所产生的约束通过合一得以求解，确定 `t4 = Int`，`t5 = Bool`，最终结果类型为 `Int`。

最终结果是 `Int`，表明 `const 42 true` 正确返回第一个参数（42），无论第二个参数的类型（true）如何。

这些接口函数展示了如何将算法 W 嵌入到更大的系统中。生成树的版本支持教学工具和调试器，而仅类型版本则提供了编译期间类型检查所需的最小接口。
