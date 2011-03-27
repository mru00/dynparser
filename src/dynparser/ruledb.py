import re

from entities import *


rules = {}

def add_rule(clazz, arg):
    global rules

    def add_inheritance(clazz2):
        sup = clazz2.__bases__[0]

        if sup == NTE:
            return

        if sup not in rules.keys():
            add_inheritance(sup)
        add_rule(sup, clazz2)


    def make_te(item):
        if type(item) == str:
            n = type("TE_" +item, (TE, object),
                     { "expression" : re.escape(item) })
            return n
        return item


    if type(arg) != list:
        arg = [ arg ]

    arg = map(make_te, arg)

    if clazz not in rules.keys():
        rules[clazz] = [ arg ]
    elif arg not in rules[clazz]:
            rules[clazz].append(arg)

    add_inheritance(clazz)


get_productions = lambda clazz: rules[clazz]


def dump_ruledb():
    global stores
    print "===dump syntax"
    for (clazz,args) in rules.items():
        print "    " + clazz.__name__ + " => " + str(args)
    print "===end dump syntax"

def reset():
    global rules
    rules = {}
