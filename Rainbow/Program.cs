//#define MAIN

namespace Rainbow;

public class Program {
#if MAIN
    [STAThread]
    public static void Main(string[] args)
    {
        if (args.Length == 0) {
            Console.WriteLine("缺少参数：path");
            return;
        }
        RbCodeObject code = new(args[0]);
        RbCodeObject.RunMainCode(code);
    }
#endif
}