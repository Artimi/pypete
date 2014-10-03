"""
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
pip install pypete

Example of usage:
----------------
::

    $ nosetests --with-pypete --pypete-prettytable --pypete-file pypete.json
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
"""
from __future__ import division
import timeit as ti
import logging
import os.path
import json
import datetime
import math

from nose.plugins.base import Plugin


log = logging.getLogger('nose.plugins.pypete')


class Pypete(Plugin):
    """
    Nose plugin for handling performance testing
    """
    name = 'pypete'

    def options(self, parser, env):
        """
        Command line options definiton
        :param parser: argparser instance
        :param env: environment
        :return:
        """
        super(Pypete, self).options(parser, env)
        parser.add_option('--pypete-repeat', action='store', dest='repeat',
                          default=3, metavar='INTEGER', type=int,
                          help='Number of times experiment should be repeated')
        parser.add_option('--pypete-number', action='store', dest='number',
                          default=0, metavar='INTEGER', type=int,
                          help='Number of times test itself should be repeated, 0 means auto')
        parser.add_option('--pypete-prettytable', action='store_true', dest='prettytable',
                          default=False,
                          help='Whether to show result in PrettyTable')
        parser.add_option('--pypete-file', action='store', dest='file',
                          default=None, metavar='FILE',
                          help='Path to file to save statistics')
        parser.add_option('--pypete-threshold', action='store', dest='threshold',
                          default=0.1, metavar='THRESHOLD', type=float,
                          help='Seconds to perform test with number set to auto')

    def configure(self, options, conf):
        """
        Function for plugin configuration
        :param options: options from command line
        :param conf:
        :return:
        """
        super(Pypete, self).configure(options, conf)
        self.repeat = options.repeat
        self.number = options.number
        self.prettytable = options.prettytable
        self.file = options.file
        self.threshold = options.threshold
        self._old_stats = None
        self.results = []

    def determine_number(self, test):
        """
        Determine number so that it is bigger than threshold
        :param test:
        :return:
        """
        init_number = 3
        x = ti.timeit(test.test, number=init_number, setup=test.test.setUp)
        number = int(math.ceil(self.threshold/(x / init_number)))
        return number

    def prepareTestCase(self, test):
        """
        Run before every test start
        :param test:
        :return:
        """
        if self.number == 0:
            number = self.determine_number(test)
        else:
            number = self.number
        timing = ti.repeat(test.test, setup=test.test.setUp,
                           repeat=self.repeat, number=number)
        stats = self._process_timing(test, timing, self.repeat, number)
        self.results.append(stats)

    def _process_timing(self, test, timing, repeat, number):
        stats = {'test': test,
                 'best': min(timing)/number,
                 'worst': max(timing)/number,
                 'average': sum(timing)/repeat/number}
        return stats

    @property
    def old_stats(self):
        """
        Loads old_stats from json file if accessible
        :return:
        """
        if self._old_stats is None and self.file and os.path.exists(self.file):
            with open(self.file) as f:
                self._old_stats = json.load(f)
        return self._old_stats

    def table_append_columns(self, table, old_test):
        """
        Append columns with values from older experiments
        :param table: PrettyTable
        :param old_test:
        :return:
        """
        def add_column(measurement):
            table.add_column('{0} [s]'.format(measurement),
                             ['{0:.6f}'.format(old_test[measurement]['best']),
                              '{0:.6f}'.format(old_test[measurement]['avg']),
                              '{0:.6f}'.format(old_test[measurement]['worst'])])
        add_column('last')
        add_column('best')
        add_column('worst')

    def get_prettytable(self, test):
        """
        Return string that contains PrettyTable with information about test
        :param test:
        :return: string with table
        """
        try:
            from prettytable import PrettyTable
        except ImportError:
            raise ImportError('PrettyTable is optional dependency. Download it or don\'t use it')
        test_id = test['test'].id()
        table = PrettyTable(['Metric', 'current [s]'])
        table.add_row(['best', '{0[best]:.6f}'.format(test)])
        table.add_row(['avg', '{0[average]:.6f}'.format(test)])
        table.add_row(['worst', '{0[worst]:.6f}'.format(test)])
        if self.old_stats is not None:
            try:
                self.table_append_columns(table, self.old_stats[test_id])
            except KeyError:
                pass
        return table.get_string()

    def report(self, stream):
        """
        Changes resulting testing output
        :param stream:
        :return:
        """
        stream.writeln('Pypete results:')
        stream.writeln('repeat = {1} and number = {2}'.format(len(self.results), self.repeat, self.number))
        if self.prettytable:
            for r in self.results:
                stream.writeln('{0}: '.format(str(r['test'])))
                stream.writeln(self.get_prettytable(r))
        else:
            for r in self.results:
                stream.writeln('{0} ... best {1[best]:.6f} s, avg {1[average]:.6f} s,'
                               ' worst {1[worst]:.6f} s'.format(str(r['test']), r))
        stream.writeln('')

    def finalize(self, result):
        """
        Ran after all tests are done. If selected file option, save results of testing
        :param result:
        :return:
        """
        if self.file:
            stats = self.get_stats()
            with open(self.file, 'w') as f:
                json.dump(stats, f, indent=2)

    def _get_dict_experiment(self, info, test):
        return {
            'info': info,
            'best': test['best'],
            'avg': test['average'],
            'worst': test['worst'],
        }

    def _new_record(self, dict_experiment):
        return {
            'last': dict_experiment,
            'best': dict_experiment,
            'worst': dict_experiment
        }

    def update_old_test(self, test_id, dict_experiment):
        """
        Update old test values with current result
        :param test_id: name of test
        :param dict_experiment: current results
        :return:
        """
        try:
            old_test = self.old_stats[test_id]
        except KeyError:
            return self._new_record(dict_experiment)
        old_test['last'] = dict_experiment
        if old_test['best']['avg'] > dict_experiment['avg']:
            old_test['best'] = dict_experiment
        if old_test['worst']['avg'] < dict_experiment['avg']:
            old_test['worst'] = dict_experiment
        return old_test

    def get_stats(self):
        """
        Return dictionary with stats to save
        :return: dict
        """
        result = {}
        current_date = str(datetime.datetime.now())
        info = {'date': current_date,
                'repeat': self.repeat,
                'number': self.number}
        for test in self.results:
            test_id = test['test'].id()
            dict_experiment = self._get_dict_experiment(info, test)
            if self.old_stats is None:
                result[test_id] = self._new_record(dict_experiment)
            else:
                result[test_id] = self.update_old_test(test_id, dict_experiment)
        return result
