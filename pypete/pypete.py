from __future__ import division
import timeit as ti
import logging
import os.path
import json
import datetime

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
                          default=10, metavar='INTEGER', type=int,
                          help='Number of times test itself should be repeated')
        parser.add_option('--pypete-prettytable', action='store_true', dest='prettytable',
                          default=False,
                          help='Whether to show result in PrettyTable')
        parser.add_option('--pypete-file', action='store', dest='file',
                          default=None, metavar='FILE',
                          help='Path to file to save statistics')

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
        self._old_stats = None
        self.results = []

    def prepareTestCase(self, test):
        """
        Run before every test start
        :param test:
        :return:
        """
        timing = ti.repeat(test.test, setup=test.test.setUp,
                           repeat=self.repeat, number=self.number)
        stats = self._process_timing(test, timing, self.repeat, self.number)
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
            except AttributeError:
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
