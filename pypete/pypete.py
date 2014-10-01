from __future__ import division
import timeit as ti
from functools import wraps, partial
from nose.plugins.base import Plugin
import logging


log = logging.getLogger('nose.plugins.pypete')

def timeit(repeat=3, number=100):
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            f_measure = partial(f, *args, **kwargs)
            result = ti.repeat(f_measure, repeat=repeat, number=number)
            return result
        return wrapped_function
    return decorator

def test_class(cls):
    '''
    Class decorator that states that this class should be tested
    '''
    class NewClass(cls):
        pypete_testing = True
    return NewClass


class Pypete(Plugin):
    '''
    Nose plugin for handling performance testing
    '''
    name = 'pypete'

    def options(self, parser, env):
        super(Pypete, self).options(parser, env)
        # TODO add options

    def configure(self, options, conf):
        super(Pypete, self).configure(options, conf)
        self.repeat = 3
        self.number = 10
        self.results = []
        self.prettytable = True

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
                raise ImportError('PrettyTable is optional dependency download it or don\'t use it')
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
