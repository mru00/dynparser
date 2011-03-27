
import parse
from entities import NTE, TE
import ruledb
import unittest
import re
import logging

logging.basicConfig(level=logging.DEBUG)




class simpletest(unittest.TestCase):

    def setUp(self):
        pass
#        ruledb.reset()
    def tearDown(self):
        ruledb.reset()

    def testSimple(self):

        class SimpleProgram(NTE): pass
        class Constant(TE):
            expression = re.compile("constant")

        ruledb.add_rule(SimpleProgram, Constant)
        x = parse.parse("constant", SimpleProgram)
        self.assertTrue( isinstance(x, SimpleProgram) )

    def testInheritance(self):

        class Statement(NTE): pass
        class ConcreteStatement(Statement): pass
        class StatementTE(TE):
            expression = re.compile(r"\w+")

        ruledb.add_rule(ConcreteStatement, StatementTE)
        x = parse.parse("constant", Statement)
        self.assertTrue( isinstance( x, ConcreteStatement) )

    def testComplex(self):
        class SimpleProgram(NTE): pass
        items = ["word1", "is", "word2", "or", "something", "else"]

        ruledb.add_rule(SimpleProgram, items)
        x = parse.parse(" ".join(items), SimpleProgram)
        for i in range(len(items)):
            self.assertEquals(items[i], x.items[i].value)

    def testComplex2(self):
        class SimpleProgram(NTE): pass

        ruledb.add_rule(SimpleProgram, [ "{", SimpleProgram, "}"] )
        ruledb.add_rule(SimpleProgram, "x")
        x = parse.parse("{{{{{x}}}}}", SimpleProgram)
        self.assertTrue(x)


    def testComplex2(self):
        class SimpleProgram(NTE): pass
        ruledb.add_rule(SimpleProgram, [ "{", SimpleProgram, "}"] )
        ruledb.add_rule(SimpleProgram, "x")
        self.assertRaises(AssertionError, parse.parse, "{{{{{x}}}}", SimpleProgram)


    def testExpression(self):
        class Expression(NTE): pass
        class Value(TE):
            expression = re.compile(r"\d+")
        ruledb.add_rule(Expression, [Value])
        ruledb.add_rule(Expression, [Expression, "+", Expression])
        ruledb.add_rule(Expression, [ "(", Expression, ")"] )
        x = parse.parse("99", Expression)
        self.assertEquals("99", x.items[0].value)


    def testExpressionPascal(self):
        # http://www.lrz.de/~bernhard/Pascal-EBNF.html
        class Expression(NTE):pass
        class SimpleExpression(NTE):pass
        class Term(NTE):pass
        class Factor(NTE):pass
        class RelationalOperator(TE):
            expression=re.compile(r"=|<|>|<=|>|>=")
        class AdditionOperator(TE):
            expression = re.compile("\+|-|or")
        class MultiplicationOperator(TE):
            expression = re.compile("\*|/|div|mod|and")
        class Variable(TE):
            expression = re.compile("\w+")
        class Number(TE):
            expression = re.compile("\d+")
        class Sign(TE):
            expression = re.compile("-|\+")

        class Rep1(NTE):pass
        class Rep2(NTE):pass
        class Rep3(NTE):pass
        ruledb.add_rule(Rep1, [ RelationalOperator, SimpleExpression ])
        ruledb.add_rule(Rep2, [ AdditionOperator, Term ])
        ruledb.add_rule(Rep3, [ MultiplicationOperator, Factor ])

        ruledb.add_rule(Expression, [ SimpleExpression, [Rep1] ])
        ruledb.add_rule(SimpleExpression, [ Term, [Rep2] ])
        ruledb.add_rule(Term, [ Factor, [Rep3] ])
        ruledb.add_rule(Factor, [ Variable ])
        ruledb.add_rule(Factor, [ Number ])
        ruledb.add_rule(Factor, [ "(", Expression, ")" ])

        parse.parse("5+4", Expression)
        parse.parse("5+((x*3) * 4-1 / 10 div y)", Expression)
        parse.parse("((x*3) * 4-1 / 10 div y)", Expression)
        parse.parse("5+((x*3) * 41 / 10 div y)", Expression)


    # def testExpression2(self):
    #     class Expression(NTE): pass
    #     class Value(TE):
    #         expression = re.compile(r"\d+")
    #     ruledb.add_rule(Expression, [Value])
    #     ruledb.add_rule(Expression, [Expression, "+", Expression])
    #     ruledb.add_rule(Expression, [ "(", Expression, ")"] )

    #     parse.parse("(99 + (453) + ( ( 2 + (1))))", Expression)


suite = unittest.TestLoader().loadTestsFromTestCase(simpletest)
unittest.TextTestRunner(verbosity=2).run(suite)
