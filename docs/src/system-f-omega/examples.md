# 示例

我们的 System Fω 实现通过一套全面的工作示例展示了其能力，这些示例全面展现了类型系统的各种特性。这些示例从基础代数数据类型逐步深入到高阶多态函数，说明 System Fω 如何在保持类型安全的同时支持高级编程模式。

这些示例既展示了实现的正确性，也实际说明了 System Fω 的理论威力如何转化为实用的编程语言特性。每个示例在我们的实现中都能成功通过类型检查，证明了算法能够处理现实世界的编程场景。

## 基本数据类型与模式匹配

我们的 System Fω 实现的基础在于支持带有全面模式匹配的代数数据类型。这些特性为更复杂的编程模式提供了构建基础。

```rust
#![source_file!("system-f-omega/examples/final_demo.hs")]
```

### 代数数据类型声明

该实现支持丰富的数据类型定义，展现了 System Fω 的 Kind 系统：

* **简单枚举**：`data Bool = True | False` 创建了一个基本和类型
* **参数化类型**：`data Maybe a = Nothing | Just a` 展示了 Kind `* -> *`
* **多参数类型**：`data Either a b = Left a | Right b` 展示了 Kind `* -> * -> *`
* **递归类型**：`data List a = Nil | Cons a (List a)` 支持归纳数据结构

每个声明都能自动推断出类型构造函数的适当 Kind，展示了实现如何透明地处理 Kind 系统。

### 类型安全的模式匹配

模式匹配提供了对代数数据类型的安全解构：

```haskell
not :: Bool -> Bool;
not b = match b {
  True -> False;
  False -> True;
};

isJust :: Maybe a -> Bool;
isJust m = match m {
  Nothing -> False;
  Just x -> True;
};
```

类型检查器会验证：
- 所有模式是否覆盖了正确的构造函数
- 模式变量是否获得了合适的类型
- 分支表达式是否具有兼容的返回类型
- 多态类型是否在各个分支中一致地处理

## 多态函数

System Fω 的全称量化使得函数能够统一地作用于所有类型，展示了参数多态的实际应用。

### 基本多态函数

```haskell
id :: a -> a;
id x = x;

const :: a -> b -> a;
const x y = x;
```

这些函数展示了：
- **类型变量作用域**：像 `a` 和 `b` 这样的变量是隐式量化的
- **主类型**：实现会推断出最通用的可能类型
- **多态实例化**：每次使用都可以以不同的方式实例化类型

### 高阶多态函数

```haskell
map :: (a -> b) -> List a -> List b;
map f lst = match lst {
  Nil -> Nil;
  Cons x xs -> Cons (f x) (map f xs);
};

fromMaybe :: a -> Maybe a -> a;
fromMaybe def m = match m {
  Nothing -> def;
  Just x -> x;
};
```

这些示例展示了：
- **函数类型作为参数**：`(a -> b)` 展示了高阶类型
- **递归多态函数**：`map` 以一致的类型调用自身
- **类型安全的默认值**：`fromMaybe` 保持了类型一致性

## 复杂多态编程

更高级的示例展示了 System Fω 如何处理多态、高阶函数与代数数据类型之间的复杂交互。

### 算术与比较运算

```haskell
add :: Int -> Int -> Int;
add x y = x + y;

multiply :: Int -> Int -> Int;
multiply x y = x * y;

lessThan :: Int -> Int -> Bool;
lessThan x y = x < y;
```

内置运算与用户定义的类型系统无缝集成，展示了原始类型如何与代数数据类型一样参与相同的类型理论框架。

### 函数组合与应用

```haskell
composed :: Int;
composed = add (multiply 6 7) 8;

listLength :: List a -> Int;
listLength lst = match lst {
  Nil -> 0;
  Cons x xs -> add 1 (listLength xs);
};
```

这些示例展示了：
- **嵌套函数应用**：复杂表达式能正确通过类型检查
- **多态递归**：`listLength` 可作用于任何类型的列表
- **类型保持**：所有中间计算都保持了类型安全

## 高级编程模式

我们的实现处理需要 System Fω 类型系统全部威力的高级编程模式。

### 构造函数应用与类型推断

```haskell
testBool :: Bool;
testBool = not True;

testMaybe :: Maybe Int;
testMaybe = Just 42;

testList :: List Int;
testList = Cons 1 (Cons 2 (Cons 3 Nil));
```

类型检查器能够正确推断构造函数应用的类型，处理：
- **类型应用**：`Just` 应用于 `42` 推断出 `Maybe Int`
- **嵌套构造函数**：复杂列表结构保持了类型一致性
- **多态实例化**：每次构造函数使用都会获得合适的类型参数

### 复杂类型的模式匹配

```haskell
either :: (a -> c) -> (b -> c) -> Either a b -> c;
either f g e = match e {
  Left x -> f x;
  Right y -> g y;
};

mapMaybe :: (a -> b) -> Maybe a -> Maybe b;
mapMaybe f m = match m {
  Nothing -> Nothing;
  Just x -> Just (f x);
};
```

这些函数展示了：
- **高阶模式匹配**：函数作为模式上下文中的参数
- **类型安全的消解**：模式匹配保持了所有类型关系
- **函子模式**：`mapMaybe` 展示了保持结构不变的变换

## 完整的示例程序

该实现包含几个完整的程序，展示了所有特性如何协同工作：

### 使用多态工具函数的斐波那契数列

一个示例程序使用多态辅助函数实现了斐波那契数列，展示了 System Fω 如何实现代码复用：

```haskell
fibonacci :: Int -> Int;
fibonacci n = match lessThan n 2 {
  True -> n;
  False -> add (fibonacci (subtract n 1)) (fibonacci (subtract n 2));
};
```

### 使用高阶函数的列表处理

另一个示例展示了使用列表的函数式编程模式：

```haskell
filter :: (a -> Bool) -> List a -> List a;
filter pred lst = match lst {
  Nil -> Nil;
  Cons x xs -> match pred x {
    True -> Cons x (filter pred xs);
    False -> filter pred xs;
  };
};

foldRight :: (a -> b -> b) -> b -> List a -> b;
foldRight f acc lst = match lst {
  Nil -> acc;
  Cons x xs -> f x (foldRight f acc xs);
};
```

## 类型推断的实际运行

这些示例展示了 DK 工作列表算法如何处理复杂的类型推断场景：

### 存在变量解析

在处理像 `map (add 1) someList` 这样的表达式时，算法：
1. **为未知类型生成存在变量**
2. **通过函数应用传播约束**
3. **统一类型**，发现列表必须具有类型 `List Int`
4. **报告最终类型**为 `List Int`

### 多态实例化

对于多次使用多态函数的表达式：
```haskell
example = (id True, id 42, id someList)
```

该算法正确地用不同类型实例化 `id`：
- `id :: Bool -> Bool` 用于第一个组件
- `id :: Int -> Int` 用于第二个组件
- `id :: List a -> List a` 用于第三个组件

### 高阶多态性

该实现能够处理接受多态参数的函数：
```haskell
applyToEach :: (forall a. a -> a) -> (Bool, Int) -> (Bool, Int);
applyToEach f (x, y) = (f x, f y);
```

这展示了该实现对高阶类型的支持，其中多态类型出现在参数位置。
