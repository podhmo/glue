def _cross_product2(xs, ys):
    r = []
    for x in xs:
        for y in ys:
            v = [e for e in x]
            v.append(y)
            r.append(v)
    return r

def cross_product(args):
    if not args:
        return args
    r = [[x] for x in args[0]]
    for ys in args[1:]:
        if ys:
            r = _cross_product2(r, ys)
    return r

class AmbLike(object):
    mzero = []
    def finish(self, x):
        return x

    def access(self, access_fn, xs):
        access_fn(self, xs)
        return xs

    def unit(self, x):
        return [x]

    def guard(self, p, xs):
        return [x for x in xs if p(self, x)]

    def join(self, xss):
        return [x for xs in xss for x in xs]

    def fmap(self, f, xs):
        return [f(self, x) for x in xs]

    def multi_fmap(self, f, xss):
        vss = cross_product(xss)
        return [f(self, *vs) for vs in vss]

    def bind(self, a_to_mb, xs):
        ## self.join(self.fmap(a_to_mb, xs) == self.bind(a_to_mb, xs)
        r = []
        for x in xs:
            r.extend(a_to_mb(self, x))
        return r

    def with_continue(self, x, cont, conts):
        return cont(self, conts, x)
