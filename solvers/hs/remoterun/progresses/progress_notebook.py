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

    def succ(self, val):
        self.progress.value = val


def test_notebook(interval=1):
    print("test for: ")

    values = [i*interval for i in range(100)]
    print(values)
    progress = ProgressNotebook(values[-1])

    for value in values:
        progress.succ(value)
