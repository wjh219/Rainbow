# Rainbow

### 简介

一种面向对象思想，易于编写的动态语言

### 下载方式

#### Windows Installer (.exe)

1. 在右侧[releases](https://github.com/wjh219/Rainbow/releases)中下载

### 示例

1. #### 最简单的程序 - hello world

    我们可以新建一个名为*test.rb*的文本文件来编写一个最简单的程序

    其中双井号`#something#`所包裹的是注释

    输入：
    `print 'Hello World!';  # 输出文本 #`

    然后在命令行输入`rainbow -r .\test.rb`便可以运行它

2. #### 基本 - variable

    直接写`var_name = value;`来创建一个变量(就像python那样)

    示例：
    ```rainbow
    tmp1 = 'Hello';
    tmp2 = 'World';
    print tmp1 + ' ' + tmp2 + '!';
    # 字符串相加 #
    ```
    输出：`>>> Hello World!`

3. #### 判断语句

+ if: 用`if expr {# code_block #}`去判断若*expr*为**true**，则执行*code_block*

+ elif：`elif expr {# code_block #}`在*if*判断为**false**时，挨个判断*elif-expr*中的内容
      
    若为**true**,则进入并执行*code_block*
     
+ else： `else {# code_block #}`
  
    在*if*之后所有*elif*都没有判断成功的情况下, 执行*else-code_block*
   
+ **写法注意**：
  
    *if*, *elif*, *else*所有被视作一个语句
    
    要在这个语句的结尾添加分号`;`
  
    示例：
    ```rainbow
    if expr {
        # do something #
    }
    elif expr1 {
       # do something #
    }
    elif expr2 {
        # do something #
    }
    else {
        # do something #
    }; # <- 注意这里 #
    ```

4. #### 循环语句
+ goto: `goto label;`

    goto会让语句跳转到label所指定的语句 (label在语句首用美元符`$`指出)
    , 如`$label a = 1;`
    
    频繁的使用goto会让代码结构变得杂乱, 但有时goto会发挥大作用

+ while: `while expr {# code_block #};`

    while循环在*expr*为**true**时进入循环, 直到*expr*为**false**为止

+ for: `for expr0, expr1, expr2 {# code_block #};`

    for循环在进入时执行*expr0*, 并判断*expr1*, 若为**true**则进入循环

    每次循环结束时执行*expr2*并判断*expr1*, 若为**true**则继续循环

+ for-each: `for var : col {# code_block #};`
    
    for-each循环会遍历*col*容器中的每一项并放入*var*中

    for-each不能修改*col*容器中的变量

5. #### 导入语句
+ import: `import path : var1, var2;` | `import path : *;`
    
    import会寻找path目录下的module中所指定的内容并导入
    可以指定星号`*`来表示导入所有

