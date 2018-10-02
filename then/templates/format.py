from then.context import Context
from then.templates.base import TemplateBase


class FormatTemplateContext(TemplateBase):
    def render(self):
        return {key: value.format(self._args) for key, value in self.context.items()}