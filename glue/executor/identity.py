class Identity(object):
    mzero = object()
    def finish(self, x):
        return x

    def access(self, access_fn, xs):
        access_fn(self, xs)
        return xs

    def unit(self, x): #identity (dont have to use it in chain())
        return x
    
    def guard(self, p, x):
        return x

    def join(self, x):
        return x

    def fmap(self, f, x):
        return f(self, x)

    def bind(self, f, ma):
        return f(self, ma)

    def multi_fmap(self, f, xs):
        return f(self, *xs)

    def with_continue(self, x, cont, conts):
        return cont(self, conts, x)
    
