import ipywidgets as widgets


class ProgressNotebook():
    def __init__(self, STEPS, prefix='progress'):

        self.step_progress = 0
        self.progress = widgets.IntProgress(
            value=self.step_progress,
            min=0,
            max=STEPS-1,
            step=1,
            description=prefix+': ',
            bar_style='',  # 'success', 'info', 'warning', 'danger' or ''
            orientation='horizontal'
        )
        self.set_prefix(prefix)

    def succ(self, val):
        self.progress.value = val

    def set_prefix(self, prefix):
        self.prefix = prefix
        self.progress.description = prefix + ": "


def test_notebook(interval=1):
    print("test for: ")

    values = [i*interval for i in range(100)]
    print(values)
    progress = ProgressNotebook(values[-1])

    for value in values:
        progress.succ(value)
