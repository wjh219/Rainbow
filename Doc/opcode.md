### 字节码

+ `LOAD_VALUE <code>` 将identifiers[code]的值放入栈顶
+ `LOAD_CONST <code>` 将consts[code]的值放入栈顶
+ `NEW_FAST <code>` 新建一个identifiers[code]变量
+ `CALL_FUNCTION` 弹出调用栈顶的方法并不断弹出栈顶作为参数最终把返回值放入栈顶

