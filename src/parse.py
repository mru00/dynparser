from entities import *
from namespace import *
from ruledb import *
import re

import logging

def parse_aux(instream, clazz, level):

    dbg = lambda m:logging.debug("%d%s[%s] %s"%(level, " "*level,clazz.__name__,m));

    if len(instream) == 0:
        return None

    instream_orig = instream[:]

    parsed_object = None

    if issubclass(clazz, TE):

        dbg("must parse TE "+clazz.__name__)
        m = re.match(clazz.expression, instream)
        dbg("testing input [truncated]: '%s'..." % instream[:20])
        if not m:
            dbg("RE '%s' does not match for input stream '%s'..." % (clazz.expression, instream[:10]))
        else:
            token = instream[m.start():m.end()]
            logging.debug("match at %s" % str(m.span()))
            possible_object = clazz()
            possible_object.value = token
            if possible_object.canparse():
                parsed_object = possible_object
                instream = instream[m.end():].strip()

    else:

        instream = instream_orig[:]

        productions = get_productions(clazz)

        dbg("trying to parse NTE with: " + str(productions))


        for production in productions:
            dbg("testing production: %s" %(production))

            assert type(production) == list, "unexpected production item: " + str(production)

            possible_object = clazz()

            for p in production:

                dbg("the current element in the production: " + str(p))

                if type(p) == list:

                    dbg("found list; parse repetition")

                    assert len(p) == 1
                    clazz3 = p[0]
                    while True:
                        subparse = parse_aux(instream, clazz3, level+1)
                        if not subparse:
                            dbg("could not parse: %s" % clazz3.__name__)
                            break
                        else:
                            (instream, x) = subparse
                            if x.canparse():
                                possible_object.add(x)
                            else:
                                break
                else:
                    assert issubclass(p, NTE) or issubclass(p,TE)

                    subparse = parse_aux(instream, p,level+1)
                    if subparse:

                        (instream, subs) = subparse

                        if subs.canparse():
                            dbg(">>parsed NTE [%s/%s]: %s" %(clazz.__name__,p.__name__, subs))
                            if isinstance(subs,clazz):
                                possible_object = subs
                            else:
                                possible_object.add(subs)
                    else:
                        possible_object = None
                        break

            parsed_object = possible_object

            if parsed_object:
                break

    if parsed_object and parsed_object.canparse():

        dbg("finishing parse of " + clazz.__name__ +
            " with parse_tree: " + parsed_object.dump())
    else:
        dbg(">>parsing NTE "+clazz.__name__+" failed, retreat")
        parsed_object = None

    if parsed_object:
        parsed_object.postparse()
        return (instream, parsed_object)

    return None


def parse(instream, toplevel):

    parse_data = parse_aux(instream, toplevel, 0)
    assert parse_data
    (instream, parse_data) = parse_data

    if len(instream) != 0:
        assert False, "parse error: not all stream consumed at: %s..." % instream[:20]

    return parse_data

