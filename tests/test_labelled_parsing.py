import unittest
from src.labelled_parsing import parse_labelled
class LabelledParsingTests(unittest.TestCase):
    def test_markdown_label(self):
        self.assertEqual(parse_labelled('`recall`: **0.250000**', ['recall']).values['recall']['value'], .25)
    def test_does_not_extract_unlabelled_numbers(self):
        self.assertEqual(parse_labelled('The answer is 0.25', ['recall']).values,{})
    def test_does_not_take_fraction_operand(self):
        self.assertEqual(parse_labelled('recall = 3 / 12 = 0.25', ['recall']).values['recall']['value'], .25)
        self.assertNotIn('recall',parse_labelled('recall = 3 / 12', ['recall']).values)
    def test_duplicate_labels_abstain(self):
        self.assertNotIn('recall',parse_labelled('recall: 0.2\nrecall: 0.3',['recall']).values)
    def test_wrong_value_preserved(self):
        self.assertEqual(parse_labelled('recall: 0.95',['recall']).values['recall']['value'], .95)
