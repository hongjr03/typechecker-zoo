# System F 类型检查器

简单λ演算加上HM风格类型方案带来了安全性和有限的多态性，但同时也非常僵化，表达能力不足。现在我们转向System F，也称为多态λ演算，它通过引入**参数化多态**打破了这一限制：能够编写一段对类型通用的代码。这是Rust、Java和C++等语言中泛型特性的理论基础，代表了表达能力的一次巨大飞跃。

为了实现这一点，System F扩展了项和类型语言。类型语言中最关键的补充是全称量词\\(\forall\\)（forall），它允许我们表达多态函数的类型。

\\[ \begin{align*} \text{types} \quad \tau &::= \alpha \mid \tau_1 \to \tau_2 \mid \forall \alpha . \tau \mid \text{Int} \mid \text{Bool} \\\\ \text{expressions} \quad e &::= x \mid \lambda x : \tau . e \mid e_1 \ e_2 \mid \Lambda \alpha . e \mid e[\tau] \mid \dots \end{align*} \\]

类型\\(\forall \alpha . \tau\\)由`Type::Forall(String, Box<Type>)`表示。项语言现在新增了两个专门处理多态的构造：

1. **类型抽象（\\(\Lambda \alpha . e\\)）**：创建多态函数。大写lambda（\\(\Lambda\\)）表示我们是对*类型变量* \\(\alpha\\)进行抽象，而非项变量。该表达式由`Expr::TAbs(String, Box<Expr>)`表示。
2. **类型应用（\\(e[\tau]\\)）**：将多态函数特化为具体类型\\(\tau\\)。这是我们使用泛型函数的方式。该表达式由`Expr::TApp(Box<Expr>, Box<Type>)`表示。

与无类型λ演算的一个关键区别在于，我们的项层抽象（\\(\lambda\\)）现在需要显式标注：\\(\lambda x : \tau . e\\)。程序员必须声明函数参数的类型。这是System F的一个标志性特征；它的强大能力是以完全类型推断为代价的，因此需要这些标注。

System F强大能力的一个经典例子是多态恒等函数`id`。现在我们能编写一个适用于任意类型\\(\alpha\\)的单一恒等函数。我们通过类型抽象创建它，并将其参数`x`赋予泛型类型\\(\alpha\\)：

\\[ \text{id} = \Lambda \alpha . \lambda x : \alpha . x \\]

这个函数的类型是\\(\forall \alpha . \alpha \to \alpha\\)。该类型表示：“对于所有类型\\(\alpha\\)，我是一个函数，接受一个\\(\alpha\\)类型的参数并返回一个\\(\alpha\\)类型的值。”

要使用这个多态函数，我们通过类型应用将其应用于一个类型。例如，要得到一个专门用于整数的恒等函数，我们将`id`应用于类型\\(\text{Int}\\)：

\\[ \text{id}[\text{Int}] \\]

这是在类型检查层面发生的计算。类型应用的结果是一个新的、特化的表达式\\(\lambda x : \text{Int} . x\\)，它拥有相应的特化类型\\(\text{Int} \to \text{Int}\\)。然后我们可以将这个特化函数应用于一个值，例如\\((\lambda x : \text{Int} . x) \ 5\\)，最终归约为\\(5\\)。这种类型层应用（\\(e[\tau]\\)）和项层应用（\\(e_1 \ e_2\\)）的分离是System F的基础。它提供了一种强大而安全的方式来编写泛型代码，但正如我们所看到的，它迫使程序员更明确地使用标注，这种权衡直接催生了更现代语言实现中使用的双向算法。

## 抽象语法树

让我们看看类型语言（`enum Type`）和项语言（`enum Expr`）的完整抽象语法树：

### 类型层面

```rust
#![enum!("system-f/src/ast.rs", Type)]
```

`Type`枚举定义了语言中所有可能类型的语法。这是我们用来描述表达式的词汇表。

*   `Type::Var(String)`：表示一个简单的类型变量，例如\\(\alpha\\)或\\(\beta\\)。它们是待定类型的占位符，常用于多态函数中。

*   `Type::ETVar(String)`：表示一个“存在类型变量”，通常写作\\(^\alpha\\)。这是一种特殊变量，由类型检查器内部使用，特别是在双向算法中。它们充当未知类型的占位符，等待算法推断。

*   `Type::Arrow(Box<Type>, Box<Type>)`：函数类型\\(\tau_1 \to \tau_2\\)。它表示一个接受第一个类型参数并返回第二个类型结果的函数。

*   `Type::Forall(String, Box<Type>)`：全称量词\\(\forall \alpha . \tau\\)。它是System F的基石，表示一个多态类型。读作：“对于所有类型\\(\alpha\\)，以下类型\\(\tau\\)成立。”其中的`String`是被绑定的类型变量\\(\alpha\\)的名称。

*   `Type::Int`和`Type::Bool`：原始类型或基类型。它们是内置于语言中的具体类型，分别表示64位整数和布尔值。

### 值层面

`Expr`枚举定义了所有可运行表达式或项的语法。这是执行计算的代码。

```rust
#![enum!("system-f/src/ast.rs", Expr)]
```

*   `Var(String)`：项层变量，如`x`或`f`。它引用作用域内的某个值，例如函数参数或`let`绑定的变量。

*   `App(Box<Expr>, Box<Expr>)`：函数应用\\(e_1 \ e_2\\)。它表示用参数\\(e_2\\)调用函数\\(e_1\\)。

*   `Abs(String, Box<Type>, Box<Expr>)`：带类型标注的λ抽象\\(\lambda x : \tau . e\\)。它定义一个匿名函数。与纯λ演算不同，参数（`String`）必须具有显式类型标注（`Box<Type>`）。最后的`Box<Expr>`是函数体。

*   `TApp(Box<Expr>, Box<Type>)`：类型应用\\(e[\tau]\\)。这是特化多态函数的机制。表达式\\(e\\)必须具有`Forall`类型，此构造将其应用于具体类型\\(\tau\\)，从而有效地“填充”泛型类型参数。

*   `TAbs(String, Box<Expr>)`：类型抽象\\(\Lambda \alpha . e\\)。这是我们创建多态函数的方式。它引入一个新的类型变量（`String`），可在表达式体（`Box<Expr>`）中使用。

*   `Ann(Box<Expr>, Box<Type>)`：类型标注\\(e : T\\)。这是向类型检查器发出的显式指令，断言表达式\\(e\\)应具有类型\\(T\\)。在双向系统中，这对于引导推断过程和解决歧义非常宝贵。

*   `LitInt(i64)` 和 `LitBool(bool)`：这些是字面量值。它们表示具体的、基本的值，这些值被“嵌入”到语言中，对应于基本类型 `Int` 和 `Bool`。它们是最简单的表达式形式，代表一个常量值。
