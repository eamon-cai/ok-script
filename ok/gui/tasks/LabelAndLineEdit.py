from qfluentwidgets import LineEdit

from ok.gui.tasks.ConfigLabelAndWidget import ConfigLabelAndWidget


class LabelAndLineEdit(ConfigLabelAndWidget):

    def __init__(self, config, config_desc, key: str):
        super().__init__(config_desc, key)
        self.key = key
        self.config = config
        self.line_edit = LineEdit()
        self.update_value()
        self.line_edit.textChanged.connect(self.value_changed)
        self.add_widget(self.line_edit)

    def update_value(self):
        self.line_edit.setText(self.config.get(self.key))

    def value_changed(self, value):
        self.config[self.key] = value
