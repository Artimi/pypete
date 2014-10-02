from __future__ import division
import timeit as ti
import logging

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
        stats = {'test': str(test),
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
                stream.writeln('{0[test]}: '.format(r))
                x = PrettyTable(['Metric', 'value [s]'])
                x.add_row(['best', '{0[best]:.6f}'.format(r)])
                x.add_row(['avg', '{0[average]:.6f}'.format(r)])
                x.add_row(['worst', '{0[worst]:.6f}'.format(r)])
                stream.writeln(x.get_string())
                stream.writeln('')
        else:
            for r in self.results:
                stream.writeln('{0[test]} ... best {0[best]:.6f} s, avg {0[average]:.6f} s, worst {0[worst]:.6f} s'.format(r))
        stream.writeln('')
