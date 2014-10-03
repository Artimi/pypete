Pypete - Python Performance Test
================================

This plugin helps writing performance tests in traditional nosetests way. To
turn it use the ``--with-pypete`` argument in running nosetests in command
line.

Plugin run tests ``number`` times and this experiment is repeated ``repeat``
times. So for measurement test will be ran ``times x repeat`` times. If ``number``
equals 0, plugin computes optimal number of tests so the time of each
experiment is bigger than ``threshold``.

I recommend to use `PrettyTable <https://code.google.com/p/prettytable/>`_
for better overview of test results. You can select file, where the results
will be stored in json format. With file and prettytable you can see
comparison of current, last, best and worst run of tests (best and worst
are according to avg value).

You can access all source codes at `my Github <https://github.com/Artimi/pypete>`_.

Install
-------
::

    pip install pypete

Example of usage:
-----------------
::

    $ nosetests --with-pypete --pypete-prettytable --pypete-file pypete.json tests/tests.py
    F..F..
    ======================================================================
    FAIL: test_fail (tests.BasicTest)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/psebek/projects/pypete/tests/tests.py", line 18, in test_fail
        self.assertTrue(False)
    AssertionError: False is not true

    ======================================================================
    FAIL: test_timed (tests.BasicTest)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/usr/lib/python2.7/site-packages/nose/tools/nontrivial.py", line 100, in newfunc
        raise TimeExpired("Time limit (%s) exceeded" % limit)
    TimeExpired: Time limit (0.001) exceeded

    Pypete results:
    repeat = 3 and number = 0
    test_fail (tests.BasicTest):
    +--------+-------------+----------+----------+-----------+
    | Metric | current [s] | last [s] | best [s] | worst [s] |
    +--------+-------------+----------+----------+-----------+
    |  best  |   0.000034  | 0.000033 | 0.000033 |  0.000033 |
    |  avg   |   0.000037  | 0.000033 | 0.000033 |  0.000036 |
    | worst  |   0.000039  | 0.000034 | 0.000034 |  0.000040 |
    +--------+-------------+----------+----------+-----------+
    test_time (tests.BasicTest):
    +--------+-------------+----------+----------+-----------+
    | Metric | current [s] | last [s] | best [s] | worst [s] |
    +--------+-------------+----------+----------+-----------+
    |  best  |   0.001184  | 0.001174 | 0.001158 |  0.001193 |
    |  avg   |   0.001186  | 0.001184 | 0.001176 |  0.001193 |
    | worst  |   0.001189  | 0.001189 | 0.001196 |  0.001193 |
    +--------+-------------+----------+----------+-----------+
    test_time2 (tests.BasicTest):
    +--------+-------------+----------+----------+-----------+
    | Metric | current [s] | last [s] | best [s] | worst [s] |
    +--------+-------------+----------+----------+-----------+
    |  best  |   0.002216  | 0.002229 | 0.002144 |  0.002257 |
    |  avg   |   0.002237  | 0.002238 | 0.002179 |  0.002276 |
    | worst  |   0.002252  | 0.002245 | 0.002201 |  0.002302 |
    +--------+-------------+----------+----------+-----------+
    test_timed (tests.BasicTest):
    +--------+-------------+----------+----------+-----------+
    | Metric | current [s] | last [s] | best [s] | worst [s] |
    +--------+-------------+----------+----------+-----------+
    |  best  |   0.010448  | 0.010492 | 0.010442 |  0.010490 |
    |  avg   |   0.010465  | 0.010541 | 0.010470 |  0.010645 |
    | worst  |   0.010474  | 0.010621 | 0.010492 |  0.010751 |
    +--------+-------------+----------+----------+-----------+
    tests.test_arguments(0.001,):
    +--------+-------------+----------+----------+-----------+
    | Metric | current [s] | last [s] | best [s] | worst [s] |
    +--------+-------------+----------+----------+-----------+
    |  best  |   0.001188  | 0.001210 | 0.001150 |  0.001205 |
    |  avg   |   0.001202  | 0.001213 | 0.001186 |  0.001219 |
    | worst  |   0.001213  | 0.001217 | 0.001205 |  0.001227 |
    +--------+-------------+----------+----------+-----------+
    tests.test_arguments(0.002,):
    +--------+-------------+----------+----------+-----------+
    | Metric | current [s] | last [s] | best [s] | worst [s] |
    +--------+-------------+----------+----------+-----------+
    |  best  |   0.002274  | 0.002250 | 0.002183 |  0.002250 |
    |  avg   |   0.002280  | 0.002262 | 0.002204 |  0.002286 |
    | worst  |   0.002288  | 0.002273 | 0.002222 |  0.002318 |
    +--------+-------------+----------+----------+-----------+

    ----------------------------------------------------------------------
    Ran 6 tests in 1.619s

    FAILED (failures=2)