class StopOnFail(object):
    mzero = None
    def stop(self):
        return self.mzero

    def finish(self, x):
        return x

    def access(self, access_fn, xs):
        access_fn(self, xs)
        return xs

    def unit(self, x): #identity (dont have to use it in chain())
        return x
    
    def guard(self, p, x):
        return x if p(self,x) else None

    def join(self, x):
        return x if x else None

    def fmap(self, f, x):
        return f(self, x) if x else None

    def bind(self, f, ma):
        if ma is None:
            return None
        return f(self, ma)

    def multi_fmap(self, f, xs):
        return f(self, *xs) if all(xs) else None

    def with_continue(self, x, cont, conts):
        if x is None:
            return None
        return cont(self, conts, x)
