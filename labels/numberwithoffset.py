from pybtex.style.labels.number import LabelStyle as NumberStyle
import six


class LabelStyle(NumberStyle):

    # def __init__(self):
    #     self.label_start = 0

    def format_labels(self, sorted_entries):
        if not hasattr(self, 'label_start'):
            raise RuntimeError('Set label_start property first')
        for number, entry in enumerate(sorted_entries):
            yield six.text_type(number + 1 + self.label_start)
