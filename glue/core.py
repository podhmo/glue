import functools
import itertools

class Glue(object):
    @classmethod
    def chain(cls, f):
        cf = ChainF(f)
        return cf

    @classmethod
    def choice(cls, *fs):
        cf = ChoiceF(fs)
        return cf

    @classmethod
    def merge(cls, *cs):
        jf =  MergeF(cs)
        return jf

    @classmethod
    def connect(cls, *ess):
        cf = ConnectF(ess)
        return cf

    @classmethod
    def tap(cls, f):
        lf = TapF(f)
        return lf

def chained_node_list_from_last(node):
    r = []
    while node:
        r.append(node)
        node = node.prev
    return reversed(r)

def call_from_start(executor, conts, *args, **kwargs):
    conts = (cont._call_cont for cont in conts)
    return conts.next()(executor, conts, *args, **kwargs)

class TapF(object):
    def __init__(self, f, prev=None):
        self.f = f
        self.prev = prev
        
    def __call__(self, executor, knil):
        conts = chained_node_list_from_last(self)
        return call_from_start(executor, conts, knil)

    def _call_cont(self, executor, conts, ma):
        try:
            cont = conts.next()
            v = executor.access(self.f, ma)
            return executor.with_continue(v, cont, conts)
        except StopIteration:
            return executor.access(self.f, ma)

    def chain(self, f):
        return ChainF(f, prev=self)

    def choice(self, *fs):
        return ChoiceF(fs, prev=self)

    def guard(self, f):
        return GuardF(f, prev=self)

    def tap(self, f):
        return TapF(f, prev=self)

    def result(self, f):
        return ResultF(f, prev=self)

class ResultF(object):
    def __init__(self, f, prev=None):
        self.f = f
        self.prev = prev

    def __call__(self, executor, knil):
        conts = chained_node_list_from_last(self)
        return call_from_start(executor, conts, knil)

    def _call_cont(self, executor, conts, v):
        return executor.finish(self.f(executor, v))

class GuardF(object):
    def __init__(self, pred, prev=None):
        self.pred = pred
        self.prev = prev

    def __call__(self, executor, knil):
        conts = chained_node_list_from_last(self)
        return call_from_start(executor, conts, knil)

    def _call_cont(self, executor, conts, ma):
        try:
            cont = conts.next()
            v = executor.guard(self.pred, ma)
            return executor.with_continue(v, cont, conts)
        except StopIteration:
            return executor.finish(executor.guard(self.pred, ma))


    def chain(self, a_to_mb):
        return ChainF(a_to_mb, prev=self)

    def choice(self, *fs):
        return ChoiceF(fs, prev=self)

    def guard(self, pred):
        return GuardF(pred, prev=self)

    def tap(self, f):
        return TapF(f, prev=self)

    def result(self, f):
        return ResultF(f, prev=self)
        

class ConnectF(object):
    def __init__(self, ess, prev=None):
        self.ess = ess
        self.prev = prev

    def __call__(self, executor, knil):
        conts = chained_node_list_from_last(self)
        return call_from_start(executor, conts, knil)

    def _call_cont(self, executor, conts, ma):
        cont = None
        for es in self.ess:
            ma = es(executor, ma)
        try: 
            cont = conts.next()
            return executor.with_continue(ma, cont, conts)
        except StopIteration:
            return executor.finish(ma)

    def chain(self, as_to_mb):
        return ChainF(as_to_mb, prev=self)

    def choice(self, *fs):
        return ChoiceF(fs, prev=self)
        
    def guard(self, as_to_mb):
        return GuardF(as_to_mb, prev=self)

    def tap(self, f):
        return TapF(f, prev=self)
        
    def result(self, f):
        return ResultF(f, prev=self)


class MergeF(object):
    def __init__(self, fs, prev=None):
        self.fs = fs #fs is [chain]
        self.prev = prev

    def __call__(self, executor, knil):
        conts = chained_node_list_from_last(self)
        return call_from_start(executor, conts, knil)

    def _call_cont(self, executor, conts, xs):
        try:
            cont = conts.next()
            vs = [f(executor, x) for f,x in itertools.izip(self.fs, xs)]
            return executor.with_continue(vs, cont, conts)
        except StopIteration:
            return [f(executor, x) for f, x in itertools.izip(self.fs, xs)]

    def chain(self, as_to_mb):
        return MergedChainF(as_to_mb, prev=self)

    def guard(self, pred):
        return GuardF(pred, prev=self)

    def result(self, f):
        return ResultF(f, prev=self)


class MergedChainF(object):
    def __init__(self, f, prev=None):
        self.f = f
        self.prev = prev

    def __call__(self, executor, *args, **kwargs):
        conts = chained_node_list_from_last(self)
        return call_from_start(executor, conts, *args, **kwargs)

    def _call_cont(self, executor, conts, mas):
        join = executor.join
        fmap = executor.multi_fmap

        try:
            cont = conts.next()
            return executor.with_continue(join(fmap(self.f, mas)), cont, conts)
        except StopIteration:
            return executor.finish(join(fmap(self.f, mas)))

    def chain(self, a_to_mb):
        return ChainF(a_to_mb, prev=self)

    def choice(self, *fs):
        return ChoiceF(fs, prev=self)

    def guard(self, pred):
        return GuardF(pred, prev=self)

    def tap(self, f):
        return TapF(f, prev=self)
        
    def result(self, f):
        return ResultF(f, prev=self)


class ChainF(object):
    def __init__(self, f, prev=None):
        self.f = f
        self.prev = prev

    def __call__(self, executor, knil):
        conts = chained_node_list_from_last(self)
        return call_from_start(executor, conts, knil)
        
    def _call_cont(self, executor, conts, ma):
        try:
            cont = conts.next()
            return executor.with_continue(executor.bind(self.f, ma), cont, conts)
        except StopIteration:
            return executor.finish(executor.bind(self.f, ma))
    
    def chain(self, a_to_mb):
        return ChainF(a_to_mb, prev=self)

    def choice(self, *fs):
        return ChoiceF(fs, prev=self)

    def guard(self, pred):
        return GuardF(pred, prev=self)

    def result(self, f):
        return ResultF(f, prev=self)
       
    def with_executor(self, executor):
        return functools.partial(self.__call__, executor)


class ChoiceF(object):
    def __init__(self, fs, prev=None):
        self.fs = fs
        self.prev = prev

    def __call__(self, executor, knil):
        conts = chained_node_list_from_last(self)
        return call_from_start(executor, conts, knil)
        
    def _call_cont(self, executor, conts, ma):
        try:
            cont = conts.next()
            for f in self.fs:
                v = executor.bind(f, ma)
                if not v == executor.mzero:
                    return executor.with_continue(v, cont, conts) 
        except StopIteration:
            for f in self.fs:
                v = executor.bind(f, ma)
                if not v == executor.mzero:
                    return executor.finish(executor.bind(f, ma))
    
    def chain(self, a_to_mb):
        return ChainF(a_to_mb, prev=self)

    def choice(self, *fs):
        return ChoiceF(fs, prev=self)

    def guard(self, pred):
        return GuardF(pred, prev=self)

    def result(self, f):
        return ResultF(f, prev=self)

