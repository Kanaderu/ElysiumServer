from django.test import TestCase
from django.test import TestCase
from django.template import Template, Context
class MathTagTestCase(TestCase):
    def test_mathtag(self):
        tests = {
            'math01': ['{% math a "$1" as result %}', {'a': 1}, '1'],
            'math02': ['{% math a b "$1 + $2" as result %}', {'a': 1, 'b': 2}, '3'],
            'math03': ['{% math a b "$1 / $2" as result %}', {'a': 1, 'b': 2}, '0'],  # NOTE: an int divides by an int
            'math04': ['{% math a b "$1 / $2" as result %}', {'a': 1.0, 'b': 2.0}, '0.5'],
            'math05': ['{% math a b "min($1, $2)" as result %}', {'a': 3, 'b': 1}, '1'],
            'math06': ['{% math a b c "($1 + $2) / $3" as result %}', {'a': 10, 'b': 10, 'c': 2}, '10'],
            'math07': ['{% math a b c "($1 ** $3) * ($2 ** $3)" as result %}', {'a': 2, 'b': 2, 'c': 2}, '16'],
            'math08': ['{% math a|length b|length 3 "($1 + $2) % $3" as result %}', {'a': range(5), 'b': range(15)}, '2'],
        }

        for name, test in tests.items():
            tag_expr, context, expected_val = test
            test_template = Template("{%% load mathtags %%}%s{{ result }}" % tag_expr, name=name)
            context = Context(context)
            try:
                self.assertEqual(test_template.render(context), expected_val)
            except AssertionError as e:
                raise AssertionError(name, *e.args)