from sklearn.base import TransformerMixin


class TextTransformer(TransformerMixin):
    def __init__(self, processing_function, patterns=None):
        self._func_to_apply = processing_function
        self.patterns = patterns

    def fit(self, x, y=None):
        return self

    def transform(self, x, y=None):
        if not self.patterns:
            transformed_x = list(map(self._func_to_apply, x))
        else:
            transformed_x = [self._func_to_apply(value, self.patterns) for value in x]

        return transformed_x
