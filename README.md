# Rainbow

### 简介
一种面向对象思想，易于编写的动态语言

### 下载方式
#### Windows Installer (.exe)
1. 在右侧[releases](https://gitee.com/hanbingqigu/rainbow/releases/)中下载

### 示例
1. #### 最简单的程序 - hello world
    我们可以新建一个名为*test.rb*的文本文件来编写一个最简单的程序

    其中双井号`#something#`所包裹的是注释

    输入：
    `print 'Hello World!';  # 输出文本 #`

    然后在命令行输入`rainbow -r .\test.rb`便可以运行它

2. #### 基本 - variable
    直接写`var_name = value;`来创建一个变量(就像python那样)
    ####
    示例：
    ```rainbow
    tmp1 = 'Hello';
    tmp2 = 'World';
    print tmp1 + ' ' + tmp2 + '!';
    # 字符串相加 #
    ```
    输出：`>>> Hello World!`

3. #### 判断语句
+ _if_, _elif_, _else_ 判断
    
    用`if expr {# code_block #}`去判断,

    若*expr*为**true**，则执行*code_block*
    ####
    elif：`elif expr {# code_block #}`

    在*if*判断为**false**时，挨个判断*elif-expr*中的内容
    
    若为**true**,则进入并执行*code_block*
    ####
    else： `else {# code_block #}`
    
    在*if*之后所有*elif*都没有判断成功的情况下, 执行*else-code_block*
    ####
    **写法注意**：

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

    程序实例:
    ```rainbow
    input '键入你的分数:' score;
    # input语句，输出第二项并把用户输入的内容保存在第三项的变量 
      本例把输入的分数保存在score变量中 #
    score = score -> int;
    # '->'为转换运算符
      此处把score(输入进来的为string类型)转换为int类型
      (int是builtins中的一个类) #
    
    # 分数判断 #
    if score >= 85 {
        print 'A';
    }
    elif score >= 60 {
        print 'B';
    }
    elif score >= 30 {
        print 'C';
    }
    else {
        print 'D';
    };
    ```
    运行结果：(其中中括号`[]`中的内容为输入的内容)
    ```rainbow
    >>> 键入你的分数:[64]
    >>> B
    ```
    ```rainbow
    >>> 键入你的分数:[12]
    >>> D
    ```
    ```rainbow
    >>> 键入你的分数:[97]
    >>> A
    ```
