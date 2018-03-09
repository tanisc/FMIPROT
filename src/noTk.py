class Tk(object):
    def __init__(self,parent):
        return False

    def update_idletasks(self,*args):
        return False

    def winfo_screenwidth(self,*args):
        return False

    def winfo_screenheight(self,*args):
        return False

    def winfo_x(self,*args):
        return False

    def winfo_y(self,*args):
        return False

    def geometry(self,*args):
        return "0x0"

    def update(self,*args):
        return False

class Text(object):
    def __init__(self,parent,yscrollcommand=0,wrap=0):
        return None

    def winfo_exists(self):
        return False

    def yview(self,parent):
        return False

    def grid(self,sticky='w'+'e'+'n'+'s',row=2,column=2,columnspan=1):
        return False

class Toplevel(object):
    def __init__(self,parent,padx=0,pady=0):
        return None

    def wm_title(self,title):
        return False

    def update_idletasks(self):
        return False

    def geometry(self,*args):
        return "100x100"



class Scrollbar(object):
    def __init__(self,parent,width=0):
        return None

    def grid(self,sticky='w'+'e'+'n'+'s',row=2,column=2,columnspan=1):
        return False

    def set(self,*args):
        return False

    def config(self,command="",*args):
        return False


class CallWrapper:
    """Internal class. Stores function to call when some user
    defined Tcl function is called e.g. after an event occurred."""
    def __init__(self, func, subst, widget):
        """Store FUNC, SUBST and WIDGET as members."""
        self.func = func
        self.subst = subst
        self.widget = widget
    def __call__(self, *args):
        """Apply first function SUBST to arguments, than FUNC."""
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except SystemExit, msg:
            raise SystemExit, msg
        except:
            self.widget._report_exception()

class IntVar(object):
    def __init__(self):
        self._x = int(0)

    def get(self):
        return self._x

    def set(self, value):
        self._x = value

    def trace(self,mode,func):
        return False

    def trace_variable(self,mode,func):
        return False

class StringVar(object):
    def __init__(self):
        self._x = ""
        self._f = None

    def get(self):
        return self._x

    def set(self, value):
        self._x = value
        if self._f is not None:
            self._f()

    def trace_variable(self,mode,callback):
        self._f = callback

    trace = trace_variable

class BooleanVar(object):
    def __init__(self):
        self._x = False

    def get(self):
        return self._x

    def set(self, value):
        self._x = value

    def trace(self,mode,func):
        return False

    def trace_variable(self,mode,func):
        return False

class DoubleVar(object):
    def __init__(self):
        self._x = float(0)

    def get(self):
        return self._x

    def set(self, value):
        self._x = value

    def trace(self,mode,func):
        return False

    def trace_variable(self,mode,func):
        return False
