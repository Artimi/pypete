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

    def report(self, stream):
        stream.writeln('Pypete results:')
        stream.writeln('repeat = {1} and number = {2}'.format(len(self.results),self.repeat, self.number))
        if self.prettytable:
            try:
                from prettytable import PrettyTable
            except ImportError:
                raise ImportError('PrettyTable is optional dependency. Download it or don\'t use it')
            for r in self.results:
                stream.writeln('{0}: '.format(str(r['test'])))
                x = PrettyTable(['Metric', 'value [s]'])
                x.add_row(['best', '{0[best]:.6f}'.format(r)])
                x.add_row(['avg', '{0[average]:.6f}'.format(r)])
                x.add_row(['worst', '{0[worst]:.6f}'.format(r)])
                stream.writeln(x.get_string())
                stream.writeln('')
        else:
            for r in self.results:
                stream.writeln('{0} ... best {1[best]:.6f} s, avg {1[average]:.6f} s, worst {1[worst]:.6f} s'.format(str(r['test']), r))
        stream.writeln('')

    def finalize(self, result):
        if self.file:
            if os.path.exists(self.file):
                with open(self.file, 'r') as f:
                    old_stats = json.load(f)
            else:
                old_stats = None
            stats = self.get_stats(old_stats)
            with open(self.file, 'w') as f:
                json.dump(stats, f, indent=2)

    def get_dict_experiment(self, info, test_stat):
        return {
            'info': info,
            'best': test_stat['best'],
            'avg': test_stat['average'],
            'worst': test_stat['worst'],
        }

    def new_record(self, dict_experiment):
        return {
            'last': dict_experiment,
            'best': dict_experiment,
            'worst': dict_experiment
        }

    def update_old_test(self, test_id, old_stats, dict_experiment):
        try:
            old_test = old_stats[test_id]
        except AttributeError:
            return self.new_record(dict_experiment)
        old_test['last'] = dict_experiment
        if old_test['best']['avg'] > dict_experiment['avg']:
            old_test['best'] = dict_experiment
        if old_test['worst']['avg'] < dict_experiment['avg']:
            old_test['worst'] = dict_experiment
        return old_test


    def get_stats(self, old_stats=None):
        result = {}
        curr_date = str(datetime.datetime.now())
        info = {'date': curr_date,
                'repeat': self.repeat,
                'number': self.number}
        for test in self.results:
            test_id = test['test'].id()
            dict_experiment = self.get_dict_experiment(info, test)
            if old_stats is None:
                result[test_id] = self.new_record(dict_experiment)
            else:
                result[test_id] = self.update_old_test(test_id, old_stats, dict_experiment)
        return result



