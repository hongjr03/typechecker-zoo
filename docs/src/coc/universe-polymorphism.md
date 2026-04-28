# 宇宙多态

宇宙多态使定义能够抽象化宇宙层级，从而创建出可在整个宇宙层级体系中工作的真正通用构造。我们的实现包含一个专用的宇宙约束求解器，可处理多态宇宙上下文中出现的复杂算术和约束关系。

## 宇宙约束求解器

```rust
#![struct!("coc/src/universe_solver.rs", UniverseSolver)]
```

`UniverseSolver` 独立于主约束求解器管理宇宙层级约束，从而能够针对宇宙算术和层级合一使用专用算法。这种分离使得高效处理宇宙多态成为可能，同时避免复杂化主要类型检查算法。

### 宇宙约束类型

宇宙约束捕捉了宇宙层级之间必须保持的逻辑一致性关系：

```rust
#![enum!("coc/src/ast.rs", UniverseConstraint)]
```

约束系统处理两种基本关系：

**相等约束**（`Equal`）要求两个宇宙层级完全相同，这源于依赖上下文中类型相等性的要求，其中宇宙层级必须精确匹配。

**排序约束**（`LessEq`）确保一个宇宙层级小于或等于另一个，从而维护防止逻辑悖论的可预测性要求。

### 宇宙约束求解

```rust
#![function!("coc/src/universe_solver.rs", UniverseSolver::solve)]
```

主求解算法通过迭代约束解析来处理约束列表，确保所有宇宙关系得到一致满足：

```rust
#![function!("coc/src/universe_solver.rs", UniverseSolver::solve_constraint)]
```

单个约束求解通过专用算法处理不同类型的约束。相等约束使用合一，而排序约束需要更复杂的分析以确保宇宙层级体系保持一致。

## 宇宙合一算法

```rust
#![function!("coc/src/universe_solver.rs", UniverseSolver::unify_universes)]
```

宇宙合一展示了处理宇宙层级算术的复杂性。该算法处理多种宇宙表达式形式：

1. **变量合一**：当将宇宙变量与任何表达式合一时，我们在执行发生检查以防止无限宇宙表达式后创建替换映射。

2. **常量合一**：宇宙常量只能与相同的常量合一，确保 `Type 0` 和 `Type 1` 等具体层级保持区分。

3. **算术表达式**：像 `u + 1` 和 `max(u, v)` 这样的宇宙表达式需要结构分解，我们递归地合一其组成宇宙表达式。

### 替换与标准化

```rust
#![function!("coc/src/universe_solver.rs", UniverseSolver::apply_substitution)]
```

宇宙替换应用展示了宇宙表达式的递归特性。当将替换应用于像 `Add` 或 `Max` 这样的复合表达式时，我们必须递归地将替换应用到所有子组件，同时保持算术结构。

### 宇宙变量的发生检查

```rust
#![function!("coc/src/universe_solver.rs", UniverseSolver::occurs_check)]
```

发生检查通过确保宇宙变量不出现在其自身解中，防止产生无限宇宙表达式。该检查必须遍历宇宙表达式的整个结构，包括算术运算和最大值表达式。

## 宇宙表达式标准化

宇宙求解器包含标准化功能，可将宇宙表达式简化为规范形式：

```rust
match u {
    Universe::Add(base, n) => {
        let base_norm = self.normalize_universe_static(base);
        match base_norm {
            Universe::Const(m) => Universe::Const(m + n),
            _ => Universe::Add(Box::new(base_norm), *n),
        }
    }
    Universe::Max(u1, u2) => {
        let u1_norm = self.normalize_universe_static(u1);
        let u2_norm = self.normalize_universe_static(u2);
        match (&u1_norm, &u2_norm) {
            (Universe::Const(n1), Universe::Const(n2)) => Universe::Const((*n1).max(*n2)),
            _ => Universe::Max(Box::new(u1_norm), Box::new(u2_norm)),
        }
    }
    _ => u.clone(),
}
```

此标准化过程：

- **算术简化**：合并加法表达式中的常量，例如 `Const(2) + 3` 变为 `Const(5)`
- **最大值计算**：计算常量之间的最大值表达式
- **规范形式**：维护标准化表达式，提高合一成功率

## 宇宙多态定义

宇宙多态支持如下定义：

```lean
def id.{u} (A : Sort u) (x : A) : A := x
```

`.{u}` 语法引入一个宇宙参数，可在不同层级实例化：

```lean
-- id 在 Type 0 实例化
id_nat : Nat → Nat := id.{0} Nat

-- id 在 Type 1 实例化
id_type : Type → Type := id.{1} Type
```

### 新鲜变量生成

```rust
#![function!("coc/src/universe_solver.rs", UniverseSolver::fresh_universe_var)]
```

新鲜宇宙变量生成确保每个宇宙抽象获得唯一变量名，防止复杂多态定义中的冲突。该算法：

1. **基本名称生成**：从描述性基本名称开始
2. **冲突避免**：检查现有变量和替换
3. **计数器扩展**：在冲突发生时添加数字后缀
4. **唯一性保证**：确保返回的名称全局唯一

### 替换管理

```rust
#![function!("coc/src/universe_solver.rs", UniverseSolver::get_substitution)]
```

求解器提供对已解析宇宙替换的访问，使主类型检查器能在整个类型检查过程中应用宇宙级解。

```rust
#![function!("coc/src/universe_solver.rs", UniverseSolver::substitute_universe)]
```

宇宙替换应用处理宇宙表达式的完整解析，递归应用所有累积的替换，生成完全解析的宇宙层级。

## 与类型检查的集成

宇宙求解器在多个点与主类型检查算法集成：

**类型形成**：在检查类型是否良好形成时，宇宙求解器确保满足宇宙层级约束。

**多态实例化**：在实例化多态定义时，宇宙求解器生成新鲜宇宙变量并维护它们之间的约束。

**定义相等性**：在检查具有宇宙多态的类型之间的定义相等性时，宇宙求解器确保宇宙关系得到保持。

### 约束满足检查

```rust
#![function!("coc/src/universe_solver.rs", UniverseSolver::is_satisfiable)]
```

可满足性检查器使类型检查器能够在提交特定类型赋值之前验证宇宙约束集是否有解。这种提前检查避免了复杂类型推理场景中的回溯。

## 宇宙多态示例

我们的实现支持多种形式的宇宙多态定义：

### 多态数据类型

```lean
structure Pair.{u, v} (A : Sort u) (B : Sort v) : Sort (max u v) :=
  (fst : A)
  (snd : B)
```

`Pair` 类型在两个宇宙层级上是多态的，结果类型位于参数宇宙层级的最大值。

### 多态函数

```lean
def const.{u, v} (A : Sort u) (B : Sort v) (x : A) (y : B) : A := x
```

`const` 函数忽略第二个参数并返回第一个参数，在两个参数类型的任意宇宙层级上均可工作。

### 宇宙层级运算

```lean
def lift.{u} (A : Sort u) : Sort (u + 1) := A
```

`lift` 操作将类型从宇宙 `u` 提升到宇宙 `u + 1`，演示了类型表达式中的宇宙层级运算。

## 失败模式

我们处理了几种失败情况，并提供自定义错误：

```rust
#![function!("coc/src/universe_solver.rs", UniverseSolver::universe_to_string)]
```

这些失败分为三种主要类型：

- **统一失败**：显示无法统一的特定宇宙层级
- **出现检查违规**：识别出无限的宇宙表达式
- **运算不一致**：指出无效的宇宙层级运算
