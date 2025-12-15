const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
  openSubtitleDialog: () => ipcRenderer.invoke('open-subtitle-dialog'),
  saveSubtitleDialog: (content) => ipcRenderer.invoke('save-subtitle-dialog', content)
});


