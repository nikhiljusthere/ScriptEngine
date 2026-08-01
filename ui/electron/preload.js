// Electron preload script - exposes IPC methods to renderer
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  // Setup commands
  runSetup: () => ipcRenderer.invoke('run-setup'),
  startServices: () => ipcRenderer.invoke('start-services'),
  stopServices: () => ipcRenderer.invoke('stop-services'),
  
  // API commands
  ingestDocument: (data) => ipcRenderer.invoke('ingest-document', data),
  generateScript: (data) => ipcRenderer.invoke('generate-script', data),
  search: (data) => ipcRenderer.invoke('search', data),
  crawlSeries: (data) => ipcRenderer.invoke('crawl-series', data),
  healthCheck: () => ipcRenderer.invoke('health-check'),
  
  // Direct IPC access for compatibility with window.electron.ipcRenderer.invoke()
  ipcRenderer: {
    invoke: (channel, data) => ipcRenderer.invoke(channel, data),
  },
  
  // Event listeners
  onSetupProgress: (callback) => {
    ipcRenderer.on('setup-progress', (event, data) => callback(data));
  },
  onSetupComplete: (callback) => {
    ipcRenderer.on('setup-complete', () => callback());
  },
  onAPILog: (callback) => {
    ipcRenderer.on('api-log', (event, data) => callback(data));
  },
  onAPIError: (callback) => {
    ipcRenderer.on('api-error', (event, data) => callback(data));
  },
  stopCrawl: () => ipcRenderer.invoke('stop-crawl'),
  checkSeriesExists: (series) =>
  ipcRenderer.invoke(
    "check-series-exists",
    series
  ),
  onCrawlProgress: (callback) => {
    const listener = (_, message) => {
      callback(message);
    };

    ipcRenderer.removeAllListeners('crawl-progress');
    ipcRenderer.on('crawl-progress', listener);

    return () => {
      ipcRenderer.removeListener('crawl-progress', listener);
    };
  },
  removeCrawlProgressListeners: () => {
    ipcRenderer.removeAllListeners('crawl-progress');
  },
    
  // Cleanup
  removeAllListeners: () => {
    ipcRenderer.removeAllListeners('setup-progress');
    ipcRenderer.removeAllListeners('setup-complete');
    ipcRenderer.removeAllListeners('api-log');
    ipcRenderer.removeAllListeners('api-error');
    ipcRenderer.removeAllListeners('stop-crawl');
    ipcRenderer.removeAllListeners('crawl-progress');
  }
});
