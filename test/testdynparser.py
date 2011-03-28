from  dynparser import parse, add_rule, reset_rules, NTE, TE
from dynparser.ruledb import dump_ruledb

import unittest
import re
import logging

logging.basicConfig(level=logging.INFO)

class simpletest(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        reset_rules()

    def testSimple(self):

        class SimpleProgram(NTE): pass
        class Constant(TE):
            expression = re.compile("constant")

        add_rule(SimpleProgram, Constant)
        x = parse("constant", SimpleProgram)
        self.assertTrue( isinstance(x, SimpleProgram) )

    def testInheritance(self):

        class Statement(NTE): pass
        class ConcreteStatement(Statement): pass
        class StatementTE(TE):
            expression = re.compile(r"\w+")

        add_rule(ConcreteStatement, StatementTE)
        x = parse("constant", Statement)
        self.assertTrue( isinstance( x, ConcreteStatement) )

    def testComplex(self):
        class SimpleProgram(NTE): pass
        items = ("word1", "is", "word2", "or", "something", "else")

        add_rule(SimpleProgram, items)
        x = parse(" ".join(items), SimpleProgram)
        for i in range(len(items)):
            self.assertEquals(items[i], x.items[i].value)

    def testComplex2(self):
        class SimpleProgram(NTE): pass

        add_rule(SimpleProgram, ( "{", SimpleProgram, "}") )
        add_rule(SimpleProgram, "x")
        x = parse("{{{{{x}}}}}", SimpleProgram)
        self.assertTrue(x)


    def testComplex2(self):
        class SimpleProgram(NTE): pass
        add_rule(SimpleProgram, ( "{", SimpleProgram, "}") )
        add_rule(SimpleProgram, "x")
        self.assertRaises(AssertionError, parse, "{{{{{x}}}}", SimpleProgram)


    def testExpression(self):
        class Expression(NTE): pass
        class Value(TE):
            expression = re.compile(r"\d+")
        add_rule(Expression, (Value,))
        add_rule(Expression, (Expression, "+", Expression))
        add_rule(Expression, ( "(", Expression, ")") )
        x = parse("99", Expression)
        self.assertEquals("99", x.items[0].value)

    # this one recurses endlessly:
    def NO___testExpression2(self):
        class Expression(NTE): pass
        class Value(TE):
            expression = re.compile(r"\d+")
        add_rule(Expression, (Value,))
        add_rule(Expression, (Expression, "+", Expression))
        add_rule(Expression, ( "(", Expression, ")") )

        parse("(99 + (453) + ( ( 2 + (1))))", Expression)


class ExpressionTests(unittest.TestCase):

    def testExpressionPascal(self):
        # http://www.lrz.de/~bernhard/Pascal-EBNF.html
        class Expression(NTE):pass
        class SimpleExpression(NTE):pass
        class Term(NTE):pass
        class Factor(NTE):pass

        class RelationalOperator(TE):     expression = r"=|<|>|<=|>|>="
        class AdditionOperator(TE):       expression = r"\+|-|or"
        class MultiplicationOperator(TE): expression = r"\*|/|div|mod|and"
        class Variable(TE):               expression = r"\w+"
        class Number(TE):                 expression = r"\d+"
        class Sign(TE):                   expression = r"-|\+"
        class SignOpt(NTE):pass

        class Rep1(NTE):pass
        class Rep2(NTE):pass
        class Rep3(NTE):pass

        add_rule(SignOpt, [Sign])
        add_rule(SignOpt, [])
        add_rule(Rep1, [ RelationalOperator, SimpleExpression ])
        add_rule(Rep2, [ AdditionOperator, Term ])
        add_rule(Rep3, [ MultiplicationOperator, Factor ])

        add_rule(Expression, [ SimpleExpression, [Rep1] ])
        add_rule(SimpleExpression, [ SignOpt, Term, [Rep2] ])
        add_rule(Term, [ Factor, [Rep3] ])
        add_rule(Factor, [ Variable ])
        add_rule(Factor, [ Number ])
        add_rule(Factor, [ "(", Expression, ")" ])

        parse("5+4", Expression)
        parse("5+((x*3) * 4-1 / 10 div y)", Expression)
        parse("((x*3) * 4-1 / 10 div y)", Expression)
        parse("5+((x*3) * 41 / 10 div y)", Expression)
        parse("-9* (-9)", Expression)
        parse("5+4+9+9+8+7", Expression)

        ## this one does not work:
        #parse("-9* -9", Expression)



class CalculatorTest(unittest.TestCase):

    def testCalculator(self):
        # simplified syntax, no expression, no relop
        class SimpleExpression(NTE):
            def calc(self):
                val = self.items[0].calc()
                for rep in self.items[1:]:
                    val = rep.items[0].calc(val, rep.items[1].calc())
                return val

        class Term(NTE):
            def calc(self):
                val = self.items[0].calc()
                for rep in self.items[1:]:
                    val = rep.items[0].calc(val, rep.items[1].calc())
                return val

        class Factor(NTE):pass
        class NumberFactor(Factor):
            def calc(self):
                return int(self.items[0].value)
        class ExpressionFactor(Factor):
            def calc(self):
                return self.items[1].calc()

        class AdditionOperator(TE):       
            expression = r"\+|-"
            def calc(self, left, right):
                return { "+" : lambda: left+right,
                         "-" : lambda: left-right }[self.value]()

        class MultiplicationOperator(TE): 
            expression = r"\*|/|mod"
            def calc(self, left, right):
                return { "*" : lambda: left*right,
                         "/" : lambda: left/right,
                         "mod": lambda: left%right}[self.value]()

        class Number(TE):                 expression = r"\d+"
        class Sign(TE):                   expression = r"-|\+"
        class SignOpt(NTE):pass

        class Rep2(NTE):pass
        class Rep3(NTE):pass

        add_rule(SignOpt, (Sign,))
        add_rule(SignOpt, ())
        add_rule(Rep2, (AdditionOperator, Term ))
        add_rule(Rep3, (MultiplicationOperator, Factor))

        add_rule(SimpleExpression, [ Term, [Rep2] ])
        add_rule(Term, [ Factor, [Rep3] ])
        add_rule(NumberFactor, [ Number ])
        add_rule(ExpressionFactor, [ "(", SimpleExpression, ")" ])

        self.assertEquals(parse("5+4", SimpleExpression).calc(), 
                          5+4)
        self.assertEquals(parse("5+4+9+9+8+7", SimpleExpression).calc(), 
                          5+4+9+9+8+7)
        self.assertEquals(parse("1*2+(5*3)+(10/2)", SimpleExpression).calc(), 
                          1*2+(5*3)+(10/2))

        self.assertEquals(parse("10/9*(10*(10))+1-1", SimpleExpression).calc(), 
                          10/9*(10*(10))+1-1)


        dump_ruledb()

suite = unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromTestCase(simpletest),
        unittest.defaultTestLoader.loadTestsFromTestCase(CalculatorTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(ExpressionTests)
        ])


unittest.TextTestRunner(verbosity=5).run(suite)
