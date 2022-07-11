using System.Collections.Generic;
using System.IO;
using System.Net.Http.Headers;
using System.Net.Mail;
using System.Runtime.CompilerServices;


namespace Rainbow;


public unsafe class RbObject {
    /*
     * 所有object的基类
     */
    public string tp_name;
    public RbObject(string tp_name) {
        this.tp_name = tp_name;
    }

    public virtual object GetValue() => "<object>";
    public virtual RbObject Add(RbObject other) => throw new NotImplementedException();
}


public class RbRef : RbObject 
{
    public int target;

    public RbRef(int target) : base("_refobject") {
        this.target = target;
    }
}


public class RbIntObject : RbObject
{
    public readonly int digit;  //数位
    public readonly int num;  //余位
    //表示 digit * 0x110000 + num

    public RbIntObject(int d, int n) : base("int")
    {
        digit = d;
        num = n;
    }
    public RbIntObject(int n) : base("int") 
    {
        digit = n / 0x110000;
        num = n % 0x110000;
    }

    public override object GetValue() => digit * 0x110000 + num;
    public override RbObject Add(RbObject other) => new RbIntObject((int)this.GetValue() + (int)other.GetValue());
}


public class RbStringObject : RbObject
{
    public readonly string value;

    public RbStringObject(string val) : base("string") => value = val;

    public override object GetValue() => value;

    public override RbObject Add(RbObject other) => new RbStringObject(this.value + (other as RbStringObject)?.value);
}


public class RbDecimalObject : RbObject
{
    public readonly RbIntObject integer;
    public readonly RbIntObject dec;
    public readonly int digit;

    public RbDecimalObject(RbIntObject i, RbIntObject d) : base("decimal")
    {
        integer = i;
        dec = d;
    }

    public override object GetValue() => 
            Convert.ToDecimal(Convert.ToString(integer.GetValue()) + "." + Convert.ToString(dec.GetValue()));
}


public class RbNoneObject : RbObject {
    public static readonly RbNoneObject None = new();
    public RbNoneObject() : base("_NoneType") { }
}


public class RbCodeObject : RbObject
{
    public List<RbObject> consts = new();
    public List<string> identifiers = new();
    public List<(int, int)> codes = new();

    public RbCodeObject(string path) : base("_CodeType")
    {
        using StreamReader sr = new(path);
        var str = sr.ReadToEnd();
        var cur = 0;
        char ch;
        consts.Add(RbNoneObject.None);
        
        while (cur < str.Length) {
            ch = str[cur];
            switch (ch) {
                case 'i':
                    ++cur;
                    int n = str[cur];
                    var id = "";
                    for (var _ = 0; _ < n; ++_) {
                        ++cur;
                        ch = str[cur];
                        id += ch;
                    }
                    identifiers.Add(id);
                    break;

                case 'n':
                    int digit, num;
                    ++cur;
                    digit = str[cur];
                    ++cur;
                    num = str[cur];
                    consts.Add(new RbIntObject(digit, num));
                    break;

                case 'f':
                    int digit1, num1, digit2, num2;
                    ++cur;
                    digit1 = str[cur];
                    ++cur;
                    num1 = str[cur];
                    ++cur;
                    digit2 = str[cur];
                    ++cur;
                    num2 = str[cur];
                    consts.Add(new RbDecimalObject(
                        new RbIntObject(digit1, num1), 
                        new RbIntObject(digit2, num2)
                        ));
                    break;

                case 's':
                    ++cur;
                    int i = str[cur];
                    var cs = "";
                    for (var _ = 0; _ < i; ++_) {
                        ++cur;
                        ch = str[cur];
                        cs += ch;
                    }
                    consts.Add(new RbStringObject(cs));
                    break;

                case 'c':
                    var code = -1;
                    var arg = -1;
                    while (cur < str.Length - 1) {
                        ++cur;
                        ch = str[cur];
                        if (code == -1)
                            code = ch;
                        else if (arg == -1)
                            arg = ch;
                        else {
                            codes.Add((code, arg));
                            code = ch;
                            arg = -1;
                        }
                    }
                    break;

                case 'b':
                    ++cur;
                    ch = str[cur];
                    consts.Add(
                        (ch == '1' ? new RbIntObject(0, 1) : new RbIntObject(0, 0))
                    );
                    break;
            }
            
            ++cur;
        }
        
        sr.Close();
    }

    public static int TARGET((int, int) code) => code.Item1;
    public static int VALUE((int, int) code) => code.Item2;

    public static RbObject BinaryOp(RbObject self, RbObject other, int code, RbFrame frame) => code switch {
        0 => self.Add(other),
        30 => frame.values[((RbRef)self).target] = other,
        _ => throw new NotImplementedException(),
    };


    public const int
        LOAD_REF = 0,
        LOAD_VALUE = 1,
        LOAD_CONST = 2,
        CALL_FUNCTION = 3,
        RETURN_VALUE = 4,
        POP_TOP = 5,
        BINARY_OP = 6,
        UNARY_OP = 7,
        JUMP_IF_TRUE = 8,
        JUMP_IF_FALSE = 9,
        JUMP_FORWARD = 10,
        NEW_FAST = 11,
        PRINT_VALUE = 12,
        INPUT_VALUE = 13,
        LOAD_NAME   = 14,
        IMPORT_NAME = 15,
        IMPORT_ALL  = 16,

        EXIT = 100;
    public static RbFrame RunMainCode(RbCodeObject code_obj) {
        var i = 0;
        var frame = new RbFrame(code_obj);
    restart:
        for (; ; ) {
            if (i >= frame.code.codes.Count)
                goto exiting;
            var code = frame.code.codes[i];
            switch (TARGET(code)) {


                case LOAD_CONST:
                    var val = VALUE(code);
                    var con = frame.code.consts[val];
                    frame.stack.Push(con);
                    break;

                case LOAD_VALUE:
                    val = VALUE(code);
                    var variable = frame.values[val];
                    if (variable == null)
                        goto error;
                    else
                        frame.stack.Push(variable);
                    break;

                case LOAD_REF:
                    val = VALUE(code);
                    var ref_obj = new RbRef(val);
                    frame.stack.Push(ref_obj);
                    break;

                case BINARY_OP:
                    val = VALUE(code);
                    var right = frame.stack.Pop();
                    var left = frame.stack.Pop();
                    var ret = BinaryOp(left, right, val, frame);
                    frame.stack.Push(ret);
                    break;

                case POP_TOP:
                    frame.stack.Pop();
                    break;

                case PRINT_VALUE:
                    var value = frame.stack.Pop();
                    Console.WriteLine(value.GetValue());
                    break;

                case INPUT_VALUE:
                    val = VALUE(code);
                    var str = frame.stack.Pop();
                    Console.Write(str.GetValue());
                    frame.values[val] = new RbStringObject(Console.ReadLine() ?? "");
                    break;

            }

            i++;
        }

    error:
        throw new Exception();
    exiting:
        return frame;
    }
}


public class RbModuleObject : RbObject {
    public string name;
    public List<string> varnames;
    public List<RbObject?> values;
    public RbModuleObject(string name, RbCodeObject code) : base("_ModuleObject") {
        this.name = name;
        var frame = RbCodeObject.RunMainCode(code);
        this.varnames = code.identifiers;
        this.values = frame.values;
    }
}



public class RbFrame {
    public Stack<RbObject> stack;
    public List<RbObject?> values;
    public RbCodeObject code;
    public RbFrame(RbCodeObject code) {
        this.stack = new();
        this.values = new();
        foreach(var _ in code.identifiers) {
            this.values.Add(null);
        }
        this.code = code;
    }
}
