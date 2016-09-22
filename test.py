from logicode import Run
import unittest
import sys

class Test(unittest.TestCase):
    def test_and(self):
        self.assertEqual(Run("1&1"), [1])
        self.assertEqual(Run("1&0"), [0])
        self.assertEqual(Run("0&1"), [0])
        self.assertEqual(Run("0&0"), [0])

    def test_or(self):
        self.assertEqual(Run("1|1"), [1])
        self.assertEqual(Run("1|0"), [1])
        self.assertEqual(Run("0|1"), [1])
        self.assertEqual(Run("0|0"), [0])

    def test_not(self):
        self.assertEqual(Run("!1"), [0])
        self.assertEqual(Run("!0"), [1])

    def test_plus(self):
        self.assertEqual(Run("1+1"), [1, 1])
        self.assertEqual(Run("1&1&1&1+1&1&1&1"), [1, 1])
        
    def test_ascii(self):
        self.assertEqual(Run("@1001000"), ["H"])
        self.assertEqual(Run("@111111+@111111"), ["?", "?"])

    def test_reverse(self):
        self.assertEqual(Run("~1"), [1])
        self.assertEqual(Run("~0101"), [1, 0, 1, 0])

    def test_heads_tails(self):
        self.assertEqual(Run("100>>"), [0])
        self.assertEqual(Run("100>"), [0, 0])
        self.assertEqual(Run("100<"), [1])

    def test_parens(self):
        self.assertEqual(Run("((1))"), [1])
        self.assertEqual(Run("((1&(1|(!0)))&1)"), [1])

    def test_nests(self):
        self.assertEqual(Run("!(1&1)&(1&0)"), [0])

    def test_chains(self):
        self.assertEqual(Run("1&1&1&1"), [1])
        self.assertEqual(Run("1&1&1&0"), [0])

    def test_multdigits(self):
        self.assertEqual(Run("11&11"), [1, 1])
        self.assertEqual(Run("!((00|10)&10)"), [0, 1])

    def test_circs(self):
        self.assertEqual(Run("circ a()->1\na()"), [1])
        self.assertEqual(Run("circ a(b)->b\na(1)"), [1])
        self.assertEqual(Run("circ a(b)->b\na(0)"), [0])
        self.assertEqual(Run("circ a(b,c)->b&c\na(0, 1)"), [0])
        self.assertEqual(Run("circ asdf(n)->cond n->1/0\nasdf(1)"), [1])
        self.assertEqual(Run("circ asdf(n)->cond n->0/1\nasdf(0)"), [1])

    def test_vars(self):
        self.assertEqual(Run("var foo=1\nfoo"), [1])
        self.assertEqual(Run("var foo=11\nfoo"), [1, 1])

    def test_conds(self):
        self.assertEqual(Run("cond 1->var foo=1/var foo=0\nfoo"), [1])
        self.assertEqual(Run("cond 1&(!1)->var foo=1/var foo=0\nfoo"), [0])


suite = unittest.TestLoader().loadTestsFromTestCase(Test)

def RunTests():
    unittest.main(defaultTest="suite", argv=[sys.argv[0]])

if __name__ == "__main__":
    RunTests()

# TODO: fix ! and + precedence
