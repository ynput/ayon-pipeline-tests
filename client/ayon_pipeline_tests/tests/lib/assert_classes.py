"""Classed and methods for comparing expected and published items in DBs"""


class DBAssert:
    @classmethod
    def count_compare(cls, queried_label, iterable, expected):
        msg = None
        no_of_docs = len(list(iterable))

        status = f"successful."
        if expected != no_of_docs:
            msg = "Expected {}, found {}".format(expected, no_of_docs)
            status = f"failed. {msg}"

        print("Comparing count of {} {}".format(queried_label, status))

        return msg
