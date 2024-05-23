"""Classed and methods for comparing expected and published items in DBs"""


class DBAssert:
    @classmethod
    def count_compare(cls, queried_label, iterable, expected):
        msg = None
        no_of_docs = len(list(iterable))
        if expected != no_of_docs:
            msg = "Not expected no of '{}'."\
                  "Expected {}, found {}".format(queried_label,
                                                 expected, no_of_docs)

        status = "successful"
        if msg:
            status = "failed"

        print("Comparing count of {} {}".format(queried_label,
                                                status))

        return msg
