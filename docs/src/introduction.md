# 类型检查动物园

这是我个人长期鼓捣的一个小项目。我们将用最简实现来复现过去五十年间最成功的静态类型系统，涵盖程序设计语言的玩具级实现及其核心类型检查算法。这些系统历经多年演变，因此我们会从简单的开始，一路深入到现代的依赖类型——本质上就是一场穿越半个世纪编程语言设计的趣味漫游。

我们选择用 Rust 实现所有这些系统，没什么特别理由，无非是 Rust 拥有不错的解析器生态且易于安装。而且我喜欢这种讽刺性的融合：在一个明确非函数式的语言中构建纯函数式语言。这有点像天堂与地狱的纠缠，至于这个隐喻的手性如何，就留给你自己判断了。

这将更像是一个有趣的周末副项目，而非对这些系统的正式介绍。若想获得权威资源，理论部分和证明请阅读 [TAPL](https://www.cis.upenn.edu/~bcpierce/tapl/)、[ATTAPL](https://www.cis.upenn.edu/~bcpierce/attapl/) 和 [PFPL](http://profs.sci.univr.it/~merro/files/harper.pdf)。每个类型检查器的主要参考文献也列在 [附录](./appendices/bibliography.md) 中。

虽然教科书和论文都很出色，但它们通常侧重于理论深度，很少涵盖在实际代码中如何布局数据结构、逻辑、抽象语法树等实现这些类型检查器的具体细节。因此，我们的目标是提供一个有趣的实现，涵盖这些系统的繁琐细节，并且能在周末完成。

示例以相当地道的 Rust 编写，包含完整的解析器和测试套件，使用了常见的编译器库如 [lalrpop](https://lalrpop.github.io/lalrpop/)、[logos](https://logos.maciej.codes/)、[ariadne](https://github.com/zesterer/ariadne) 等。它们显然是完整实现的简化版和代码高尔夫版本，以便轻松理解和修改。但相比阅读生产级实现，它们应该容易理解得多。解析也是已解决的问题，[cranelift](https://cranelift.dev) 和 [MLIR](https://www.stephendiehl.com/posts/mlir_introduction/) 已经存在，所以我不会过多关注这方面，因为越来越多的工作被委派给库来完成。

完整源代码以 MIT 许可证在 Github 上提供：

* [**Github 源代码**](https://github.com/sdiehl/typechecker-zoo)
* [构建说明](https://github.com/sdiehl/typechecker-zoo/blob/main/README.md)

***

既然这是一个类型检查“动物园”，而且我们目标是在“函数式”中注入“趣味”，每个类型检查器都会有一个动物吉祥物。我们将构建的四个小生灵是：

<div class="type-system-section">
<a href="./algorithm-w/lambda-calculus.html">
<img src="lambda.png" alt="Lambda 演算符号" class="type-system-logo">
</a>

[**算法 W**](./algorithm-w/lambda-calculus.html) *(775 行代码)*

Robin Milner 的经典 Hindley-Milner 类型推断算法，来自《编程中的类型多态性理论》。一个玩具级 **多态 lambda 演算**。
</div>

<div class="type-system-section">
<a href="./system-f/system-f.html">
<img src="ocaml.png" alt="OCaml logo" class="type-system-logo">
</a>

[**系统 F**](./system-f/system-f.html) *(1090 行代码)*

带有参数多态性的二阶 lambda 演算，使用双向类型检查。一个 **Mini-OCaml**。

实现了 Dunfield 和 Krishnaswami 的《高阶多态性的完整且简单的双向类型检查》中的 DK 算法。
</div>

<div class="type-system-section">
<a href="./system-f-omega/system-f-omega.html">
<img src="haskell.png" alt="Haskell logo" class="type-system-logo">
</a>

[**系统 Fω**](./system-f-omega/system-f-omega.html) *(3196 行代码)*

完整的系统 Fω 实现，包含高阶类型、双向类型检查、存在类型变量、多态构造函数应用、模式匹配和数据类型。一个 **Haskell-lite**。

使用了 Zhao 等人的《高阶多态类型推断的机械化形式化》中的方法。
</div>

<div class="type-system-section">
<a href="./coc/calculus-of-constructions.html">
<img src="lean.png" alt="Lean logo" class="type-system-logo">
</a>

[**构造演算**](./coc/calculus-of-constructions.html) *(6000 行代码)*

带有可数非累积宇宙层级和归纳类型的构造演算。一个 **迷你 Lean 风格的依赖类型检查器**。

实现了 Vladimir Voevodsky 在《宇宙多态类型系统》中概述的双向依赖类型检查器。
</div>

这是一个 MIT 许可的项目，只是我业余时间的爱好。如果你在散文或代码中发现错别字，欢迎在 [Github 上发起拉取请求](https://github.com/sdiehl/typechecker-zoo)，我将不胜感激！
