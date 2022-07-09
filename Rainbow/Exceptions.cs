using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Rainbow;

public abstract class RbBaseException {
    public abstract string Message { get; set; }
    public abstract int Code { get; set; }
}
