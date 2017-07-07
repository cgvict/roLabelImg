<!--
    Please provide as much as detail and example as you can.
    You can add screenshots if appropriate.
-->

### issue1

- **OS:** mac os

- **PyQt version:** 5

- **Error:** Segmentation fault: 11

- **Solution**: open labelImg.py, go to line 175, comment this line.
```
        self.filedock.setWidget(fileListContainer)

        self.zoomWidget = ZoomWidget()
        # self.colorDialog = ColorDialog(parent=self)

        self.canvas = Canvas()
```