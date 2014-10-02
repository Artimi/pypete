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
        super(Pypete, self).configure(options, conf)
        self.repeat = options.repeat
        self.number = options.number
        self.prettytable = options.prettytable
        self.file = options.file
        self._old_stats = None
        self.results = []

    def prepareTestCase(self, test):
        timing = ti.repeat(test.test, setup=test.test.setUp,
                           repeat=self.repeat, number=self.number)
        stats = self.process_timing(test, timing, self.repeat, self.number)
        self.results.append(stats)

    def process_timing(self, test, timing, repeat, number):
        stats = {'test': test,
                 'best': min(timing)/number,
                 'worst': max(timing)/number,
                 'average': sum(timing)/repeat/number}
        return stats

    @property
    def old_stats(self):
        if self._old_stats is None and self.file and os.path.exists(self.file):
            with open(self.file) as f:
                self._old_stats = json.load(f)
        return self._old_stats

    def table_append_collumns(self, table, old_test):
        def add_column(measurement):
            table.add_column('{0} [s]'.format(measurement),
                             ['{0:.6f}'.format(old_test[measurement]['best']),
                              '{0:.6f}'.format(old_test[measurement]['avg']),
                              '{0:.6f}'.format(old_test[measurement]['worst'])])
        add_column('last')
        add_column('best')
        add_column('worst')

    def get_prettytable(self, r):
        try:
            from prettytable import PrettyTable
        except ImportError:
            raise ImportError('PrettyTable is optional dependency. Download it or don\'t use it')
        test_id = r['test'].id()
        table = PrettyTable(['Metric', 'current [s]'])
        table.add_row(['best', '{0[best]:.6f}'.format(r)])
        table.add_row(['avg', '{0[average]:.6f}'.format(r)])
        table.add_row(['worst', '{0[worst]:.6f}'.format(r)])
        if self.old_stats is not None:
            try:
                self.table_append_collumns(table, self.old_stats[test_id])
            except AttributeError:
                pass
        return table.get_string()

    def report(self, stream):
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
        if self.file:
            stats = self.get_stats()
            with open(self.file, 'w') as f:
                json.dump(stats, f, indent=2)

    def get_dict_experiment(self, info, test):
        return {
            'info': info,
            'best': test['best'],
            'avg': test['average'],
            'worst': test['worst'],
        }

    def new_record(self, dict_experiment):
        return {
            'last': dict_experiment,
            'best': dict_experiment,
            'worst': dict_experiment
        }

    def update_old_test(self, test_id, dict_experiment):
        try:
            old_test = self.old_stats[test_id]
        except KeyError:
            return self.new_record(dict_experiment)
        old_test['last'] = dict_experiment
        if old_test['best']['avg'] > dict_experiment['avg']:
            old_test['best'] = dict_experiment
        if old_test['worst']['avg'] < dict_experiment['avg']:
            old_test['worst'] = dict_experiment
        return old_test

    def get_stats(self):
        result = {}
        current_date = str(datetime.datetime.now())
        info = {'date': current_date,
                'repeat': self.repeat,
                'number': self.number}
        for test in self.results:
            test_id = test['test'].id()
            dict_experiment = self.get_dict_experiment(info, test)
            if self.old_stats is None:
                result[test_id] = self.new_record(dict_experiment)
            else:
                result[test_id] = self.update_old_test(test_id, dict_experiment)
        return result
