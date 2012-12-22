import unittest

class StopOnFailTests(unittest.TestCase):
    def _get_target(self):
        from glue import Glue
        return Glue

    def _get_executor(self):
        from glue.executor.stoponfail import StopOnFail
        return StopOnFail()

    def test_simple(self):
        target = self._get_target()
        executor = self._get_executor()
        result = target.chain(lambda c, x: x * 10)(executor, 100)
        self.assertEquals(result, 1000)

    def test_simple_with_None(self):
        target = self._get_target()
        executor = self._get_executor()
        result = target.chain(lambda c, x: x * 10)(executor, None)
        self.assertEquals(result, None)
        

    def test_two_chain(self):
        target = self._get_target()
        executor = self._get_executor()
        result = target.chain(lambda c, x: x * 10).chain(lambda c, x: x + 10)(executor, 100)
        self.assertEquals(result, 1010)


    def test_reuse_chained_variable(self):
        target = self._get_target()
        executor = self._get_executor()
        inc = lambda c,x : c.unit(x+1)

        xs = target.chain(inc).chain(inc)
        add3 = xs.chain(inc)
        add2_mul10 = xs.chain(lambda c,x: x * 10)

        self.assertEqual(add3(executor,10), 13)
        self.assertEqual(add3(executor, None), None)
        self.assertEqual(add2_mul10(executor,10), 120)

    def test_guard_return_true(self):
        target = self._get_target()
        executor = self._get_executor()

        result = target.chain(lambda c,x: c.unit(x*x)).guard(lambda c,x: x % 2 == 0)(executor, 10)
        self.assertEqual(result, 100)

    def test_guard_return_false(self):
        target = self._get_target()
        executor = self._get_executor()

        result = target.chain(lambda c,x: c.unit(x*x)).guard(lambda c,x: x % 2 == 0)(executor, 11)
        self.assertEqual(result, None)

    def test_chain_guard_chain(self):
        target = self._get_target()
        executor = self._get_executor()

        sq_guard_tri = target.chain(lambda c,x: c.unit(x*x))\
            .guard(lambda c,x: x % 2 == 0)\
            .chain(lambda c,x: c.unit(x*x*x))

        self.assertEqual(sq_guard_tri(executor, 1), None)
        self.assertEqual(sq_guard_tri(executor, 2), 64)

    def test_merge(self):
        target = self._get_target()
        executor = self._get_executor()
        result = target.merge(target.chain(lambda c, x: x * 3), 
                              target.chain(lambda c, y: y * 5),
                              target.chain(lambda c, z: z * 7))\
                              (executor, [100,10,1])
        self.assertEquals(result, [300,50,7])
        
    def test_merge_and_chain(self):
        target = self._get_target()
        executor = self._get_executor()
        result = target.merge(target.chain(lambda c, x: x * 3), 
                              target.chain(lambda c, y: y * 5),
                              target.chain(lambda c, z: z * 7))\
                              .chain(lambda c,x,y,z: [x,y,x,y,z])(executor, [100,10,1])
        self.assertEquals(result,[300,50,300,50,7])

    def test_merge_and_chain_with_None(self):
        target = self._get_target()
        executor = self._get_executor()
        result = target.merge(target.chain(lambda c, x: x * 3), 
                              target.chain(lambda c, y: y * 5),
                              target.chain(lambda c, z: z * 7))\
                              .chain(lambda c,x,y,z: None)(executor, [100,10,1])
        self.assertEquals(result, None)

    def test_merge_and_two_chain(self):
        target = self._get_target()
        executor = self._get_executor()
        result = target.merge(target.chain(lambda c, x: x * 3), 
                              target.chain(lambda c, y: y * 5),
                              target.chain(lambda c, z: z * 7))\
                              .chain(lambda c,x,y,z: [x,y,x,y,z])\
                              .chain(lambda c, xs : sum(xs))(executor, [100,10,1])
        self.assertEquals(result, 707)

    def test_connect(self):
        target = self._get_target()
        executor = self._get_executor()
        add3 = target.chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1))

        result = add3(executor, 10)
        self.assertEqual(result, 13)

    def test_connect_connect(self):
        target = self._get_target()
        executor = self._get_executor()
        add3 = target.chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1))

        result = target.connect(add3,add3,add3,add3)(executor, 10)
        self.assertEqual(result, 22)

    def test_connect_connect_chain(self):
        target = self._get_target()
        executor = self._get_executor()
        add3 = target.chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1))

        result = target.connect(add3,add3,add3,add3).chain(lambda c,x: c.unit(x-1))(executor, 10)
        self.assertEqual(result, 21)

    def test_choice(self):
        target = self._get_target()
        executor = self._get_executor()
        must_failure = target.choice(lambda c,x: None, lambda c,x: None)
        self.assertEqual(must_failure(executor, 10), None)

        must_success = target.choice(lambda c,x: None, lambda c,x: x * x)
        self.assertEqual(must_success(executor, 10), 100)

        first_is_select = target.choice(lambda c,x: x+1, lambda c,x: x * x)
        self.assertEqual(first_is_select(executor, 10), 11)
        

    def test_tap(self):
        target = self._get_target()
        executor = self._get_executor()

        result = target.tap(lambda m,x: m.__setattr__("sq", x*x)).chain(lambda c,x: c.sq * x)(executor, 10)
        self.assertEqual(result, 1000)

    def test_result(self):
        target = self._get_target()
        executor = self._get_executor()

        result = target.tap(lambda m,x: m.__setattr__("sq", x*x)).result(lambda c,x: [x, c.sq])(executor, 10)
        self.assertEqual(result, [10,100])


class AmbLikeTests(unittest.TestCase):
    def _get_target(self):
        from glue import Glue
        return Glue
    def _get_executor(self):
        from glue.executor.amblike import AmbLike
        return AmbLike()

    def test_simple(self):
        target = self._get_target()
        executor = self._get_executor()
        result = target.chain(lambda c,x: c.unit(x * x))(executor, [1,2,3])
        self.assertEquals(result, [1,4,9])

    def test_two_chain(self):
        target = self._get_target()
        executor = self._get_executor()
        result = target.chain(lambda c,x: c.unit(x * x)).chain(lambda c,x: c.unit(x * 10))(executor, [1,2,3])
        self.assertEquals(result, [10,40,90])

    def test_reuse_chained_variable(self):
        target = self._get_target()
        executor = self._get_executor()
        inc = lambda c,x : c.unit(x+1)

        xs = target.chain(inc).chain(inc)
        add3 = xs.chain(inc)
        add2_mul10 = xs.chain(lambda c,x: c.unit(x * 10))
        self.assertEqual(add3(executor, [1,2,3]), [4,5,6])
        self.assertEqual(add2_mul10(executor, [1,2,3]), [30,40,50])

    def test_guard(self):
        target = self._get_target()
        executor = self._get_executor()

        result = target.chain(lambda c,x: c.unit(x*x)).guard(lambda c,x: x % 2 == 0)(executor, [10,11,12])
        self.assertEqual(result, [100,144])

    def test_chain_guard_chain(self):
        target = self._get_target()
        executor = self._get_executor()

        result = target.chain(lambda c,x: c.unit(x*x))\
            .guard(lambda c,x: x % 2 == 0)\
            .chain(lambda c,x: c.unit(x*x*x))(executor, [1,2,3,4,5,6])
        self.assertEqual(result, [64,4096,46656])

    def test_merge(self):
        target = self._get_target()
        executor = self._get_executor()
        result = target.merge(target.chain(lambda c, x: c.unit(x * 3)), 
                              target.chain(lambda c, y: c.unit(y * 5)),
                              target.chain(lambda c, z: c.unit(z * 7)))\
                              (executor, [[100,200, 300],[10],[1]])
        self.assertEquals(result, [[300,600,900],[50],[7]])
        
    def test_merge_and_chain(self):
        target = self._get_target()
        executor = self._get_executor()

        result = target.merge(target.chain(lambda c, x: c.unit(x * 3)), 
                              target.chain(lambda c, y: c.unit(y * 5)),
                              target.chain(lambda c, z: c.unit(z * 7)))\
                              .chain(lambda c, x,y,z: c.unit(x+y+z))(executor, [[100,200, 300],[10],[1]])
        self.assertEquals(result,[357,657,957])


    def test_connect(self):
        target = self._get_target()
        executor = self._get_executor()
        add3 = target.chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1))

        result = add3(executor, [1,2,3])
        self.assertEqual(result,[4,5,6])

    def test_connect_connect(self):
        target = self._get_target()
        executor = self._get_executor()
        add3 = target.chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1))

        result = target.connect(add3,add3,add3,add3)(executor, [1,2,3])
        self.assertEqual(result, [13,14,15])

    def test_connect_connect_chain(self):
        target = self._get_target()
        executor = self._get_executor()
        add3 = target.chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1)).chain(lambda c,x: c.unit(x+1))

        result = target.connect(add3,add3,add3,add3).chain(lambda c,x: c.unit(x-1))(executor, [1,2,3])
        self.assertEqual(result, [12,13,14])

    def test_result(self):
        target = self._get_target()
        executor = self._get_executor()

        result = target.tap(lambda m,xs: m.__setattr__("prev", xs))\
            .chain(lambda c,x: c.unit(x * x))\
            .result(lambda c,xs: ["prev", c.prev, "result", xs])(executor, [10,20,30])
        self.assertEqual(result,["prev", [10,20,30], "result", [100,400,900]])


if __name__ == "__main__":
    unittest.main()

