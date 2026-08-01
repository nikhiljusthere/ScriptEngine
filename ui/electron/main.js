/**
 * Anime Script AI - Desktop Application Entry Point
 *
 * This is the main launcher that handles:
 * 1. Environment detection (Windows/Mac/Linux)
 * 2. Automatic setup (Docker, Python deps, models)
 * 3. Starting all services
 * 4. Launching the UI
 */

const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");
const fs = require("fs-extra");
const { spawn, exec } = require("child_process");
const axios = require("axios");

const ROOT_DIR = path.join(__dirname, "..", "..");
const UI_DIR = path.join(__dirname, "..");
const APP_PATHS = require(path.join(ROOT_DIR, "constants.json"));
const API_BASE = APP_PATHS.api_base_url || "http://localhost:8000";

let crawlerProcess = null;
let crawlerStopRequested = false;
let mainWindow;
let apiProcess = null;
let setupComplete = false;

// ==================== SETUP FUNCTIONS ====================

async function detectOS() {
  const platform = process.platform;

  if (platform === "win32") return "windows";
  if (platform === "darwin") return "macos";
  if (platform === "linux") return "linux";

  throw new Error(`Unsupported OS: ${platform}`);
}

async function getPythonCommand() {
  try {
    await execCommand(await detectOS(), "python --version");

    return "python";
  } catch {
    return "python3";
  }
}

async function checkDocker() {
  const os = await detectOS();

  try {
    const result = await execCommand(os, "docker --version");
    if (result.includes("Docker version")) {
      return true;
    }
  } catch (error) {
    // Docker not found
  }

  return false;
}

async function checkPython() {
  const os = await detectOS();

  try {
    const result = await execCommand(os, "python --version");
    if (result.includes("Python")) {
      return true;
    }
  } catch (error) {
    // Try python3
    try {
      const result = await execCommand(os, "python3 --version");
      if (result.includes("Python")) {
        return true;
      }
    } catch (e) {
      return false;
    }
  }

  return false;
}

async function checkNode() {
  const os = await detectOS();

  try {
    const result = await execCommand(os, "node --version");
    if (result.includes("v")) {
      return true;
    }
  } catch (error) {
    return false;
  }

  return false;
}

async function checkOllama() {
  const os = await detectOS();

  try {
    const result = await execCommand(os, "ollama --version");
    if (result.includes("ollama version")) {
      return true;
    }
  } catch (error) {
    return false;
  }

  return false;
}

async function checkGit() {
  const os = await detectOS();

  try {
    const result = await execCommand(os, "git --version");
    if (result.includes("git version")) {
      return true;
    }
  } catch (error) {
    return false;
  }

  return false;
}

// ==================== EXECUTE COMMANDS ====================

function execCommand(os, command, cwd = null) {
  return new Promise((resolve, reject) => {
    const shell = os === "windows" ? "powershell.exe" : "bash";
    const args =
      os === "windows" ? ["-NoProfile", "-Command", command] : ["-c", command];

    const process = spawn(shell, args, {
      cwd: cwd || ROOT_DIR,
      shell: true,
    });

    let output = "";
    let errorOutput = "";

    process.stdout.on("data", (data) => {
      output += data.toString();

      // Send progress to UI
      mainWindow?.webContents.send("setup-progress", {
        type: "output",
        message: data.toString().trim(),
      });
    });

    process.stderr.on("data", (data) => {
      errorOutput += data.toString();

      mainWindow?.webContents.send("setup-progress", {
        type: "error",
        message: data.toString().trim(),
      });
    });

    process.on("close", (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(`Command failed with code ${code}: ${errorOutput}`));
      }
    });
  });
}

// ==================== SETUP STEPS ====================

async function runFullSetup() {
  const os = await detectOS();

  // Step 1: Check prerequisites
  mainWindow?.webContents.send("setup-progress", {
    type: "info",
    message: "🔍 Checking system requirements...",
  });

  // Docker is no longer checked: the graph and lexical index live in SQLite and
  // the vector store runs in Qdrant local mode, so there are no services to start.
  const checks = {
    python: await checkPython(),
    node: await checkNode(),
    ollama: await checkOllama(),
    git: await checkGit(),
  };

  mainWindow?.webContents.send("setup-progress", {
    type: "info",
    message: `✅ System checks complete`,
  });

  // Step 2: Install Node dependencies
  if (!checks.node) {
    throw new Error(
      "Node.js is required. Please install Node.js from https://nodejs.org",
    );
  }

  mainWindow?.webContents.send("setup-progress", {
    type: "info",
    message: "📦 Installing Node dependencies...",
  });

  await execCommand(os, "npm install", ROOT_DIR);

  // Step 2: Install UI dependencies
  mainWindow?.webContents.send("setup-progress", {
    type: "info",
    message: "🎨 Building React UI...",
  });

  await execCommand(os, "npm install", UI_DIR);

  // Step 3: Build UI
  mainWindow?.webContents.send("setup-progress", {
    type: "info",
    message: "🏗️ Building UI...",
  });

  await execCommand(os, "npm run build", UI_DIR);

  // Step 4: Install Python dependencies (if needed)
  if (checks.python) {
    mainWindow?.webContents.send("setup-progress", {
      type: "info",
      message: "🐍 Installing Python dependencies...",
    });

    await execCommand(os, "pip install -r requirements.txt");


  }

  // spaCy is deliberately not installed here. The factual backbone comes from
  // wikitext infoboxes and wikilinks, which need no NER; spaCy is an optional
  // booster for prose-only relations. Note the old call also referenced
  // `checks.os`, which never existed on the checks object.


  // Step 6: Pull Ollama model (if Ollama available)
  if (checks.ollama) {
    mainWindow?.webContents.send("setup-progress", {
      type: "info",
      message: "🤖 Downloading LLM model (this may take a while)...",
    });

    // Model pull is left to the user: ScriptEngine only needs an LLM for
    // optional summarisation and eval scoring, and the choice of Qwen or Gemma
    // (and its size) depends on what else is holding VRAM at the time.
  }

  // Step 7: Start API server
  mainWindow?.webContents.send("setup-progress", {
    type: "info",
    message: "🚀 Starting API server...",
  });

  startAPIServer();

  setupComplete = true;

  mainWindow?.webContents.send("setup-complete");
}

async function startAPIServer() {
  const os = require("os").platform();
  const pythonCmd = await getPythonCommand();

  apiProcess = spawn(pythonCmd, ["-m", "scriptengine.api.main"], {
    cwd: ROOT_DIR,
    shell: true,
    stdio: ["pipe", "pipe", "pipe"],
  });

  apiProcess.stdout.on("data", (data) => {
    mainWindow?.webContents.send("api-log", data.toString());
  });

  apiProcess.stderr.on("data", (data) => {
    mainWindow?.webContents.send("api-error", data.toString());
  });

  apiProcess.on("close", (code) => {
    mainWindow?.webContents.send("api-stopped");
  });
}

// ==================== IPC HANDLERS ====================

function setupIPC() {
  console.log("Setting up IPC handlers...");

  // Setup commands
  ipcMain.handle("run-setup", async () => {
    try {
      await runFullSetup();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // Start services manually
  ipcMain.handle("start-services", async () => {
    try {
      startAPIServer();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });

  // Stop services
  ipcMain.handle("stop-services", async () => {
    if (apiProcess) {
      apiProcess.kill();
      apiProcess = null;
    }

    // Nothing else to stop: the stores are files, not services.
    return { success: true };
  });

  // These call the FastAPI service in scriptengine/api/main.py. The paths here
  // used to be /api/v1/... against a server that was never written, so every
  // one of these buttons failed silently.

  ipcMain.handle("list-series", async () => {
    try {
      const response = await axios.get(`${API_BASE}/series`);
      return response.data;
    } catch (error) {
      throw new Error(`Could not list series: ${error.message}`);
    }
  });

  // The bundle a script-writing model consumes: ordered passages, the facts
  // behind them, and a citation each.
  ipcMain.handle("get-context", async (event, data) => {
    try {
      const response = await axios.post(`${API_BASE}/context`, data, {
        timeout: 300000,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Context request failed: ${error.message}`);
    }
  });

  ipcMain.handle("get-timeline", async (event, { series, subject }) => {
    try {
      const response = await axios.get(
        `${API_BASE}/timeline/${encodeURIComponent(series)}/${encodeURIComponent(subject)}`,
        { timeout: 300000 },
      );
      return response.data;
    } catch (error) {
      throw new Error(`Timeline request failed: ${error.message}`);
    }
  });

  ipcMain.handle("get-facts", async (event, { series, entity }) => {
    try {
      const response = await axios.get(
        `${API_BASE}/facts/${encodeURIComponent(series)}/${encodeURIComponent(entity)}`,
      );
      return response.data;
    } catch (error) {
      throw new Error(`Facts lookup failed: ${error.message}`);
    }
  });

  ipcMain.handle("search", async (event, data) => {
    try {
      const response = await axios.post(`${API_BASE}/search`, data, {
        timeout: 300000,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Search failed: ${error.message}`);
    }
  });

  ipcMain.handle("check-series-exists", async (_, series) => {
    const safeSeries = series.replace(/[\\/:*?"<>|]/g, "_");

    const folder = path.join(
      ROOT_DIR,
      APP_PATHS.crawl_ingestion_data_dir,
      safeSeries,
    );

    if (!fs.existsSync(folder)) {
      return {
        exists: false,
        fileCount: 0,
      };
    }

    const files = fs
      .readdirSync(folder)
      .filter((f) => f.endsWith(".txt") || f.endsWith(".html"));

    return {
      exists: true,
      fileCount: files.length,
    };
  });

  // Crawl series
  ipcMain.handle("crawl-series", async (event, data) => {
    if (crawlerProcess) {
      return {
        success: false,
        running: true,
        message: "A crawl is already running.",
      };
    }

    const pythonCmd = await getPythonCommand();
    return new Promise((resolve, reject) => {
      crawlerStopRequested = false;
      const crawlerArgs = [
        "-m",
        "scriptengine.cli",
        "crawl",
        "--series",
        data.series,
        "--start-url",
        data.url,
      ];

      if (data.output_format) {
        crawlerArgs.push("--output-format", data.output_format);
      }

      if (data.max_pages) {
        crawlerArgs.push("--max-pages", String(data.max_pages));
      }

      crawlerProcess = spawn(
        pythonCmd,
        crawlerArgs,
        {
          cwd: ROOT_DIR,
          shell: false,
          detached: process.platform !== "win32",
        },
      );

      let output = "";
      let errorOutput = "";

      crawlerProcess.stdout.on("data", (chunk) => {
        const text = chunk.toString();

        output += text;

        mainWindow?.webContents.send("crawl-progress", text);
      });

      crawlerProcess.stderr.on("data", (chunk) => {
        const text = chunk.toString();

        errorOutput += text;

        mainWindow?.webContents.send("crawl-progress", text);
      });

      crawlerProcess.on("close", (code) => {
        crawlerProcess = null;

        if (crawlerStopRequested) {
          crawlerStopRequested = false;
          resolve({
            success: false,
            stopped: true,
            output: output + errorOutput,
            stdout: output,
            stderr: errorOutput,
          });
          return;
        }

        if (code === 0) {
          resolve({
            success: true,
            output: output + errorOutput,
            stdout: output,
            stderr: errorOutput,
          });
        } else {
          reject(new Error(errorOutput || output || `Crawler exited with code ${code}`));
        }
      });
    });
  });

  // Health check
  ipcMain.handle("health-check", async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`);
      return response.data;
    } catch (error) {
      return { status: "unhealthy", services: {} };
    }
  });

  console.log("[IPC] All handlers registered:", [
    "run-setup",
    "start-services",
    "stop-services",
    "list-series",
    "get-context",
    "get-timeline",
    "get-facts",
    "search",
    "crawl-series",
    "health-check",
  ]);
}

ipcMain.handle("stop-crawl", async () => {
  if (!crawlerProcess) {
    return { success: true };
  }

  try {
    console.log("Stopping crawler PID:", crawlerProcess.pid);
    crawlerStopRequested = true;

    if (process.platform === "win32") {
      exec(`taskkill /PID ${crawlerProcess.pid} /T /F`);
    } else {
      try {
        process.kill(-crawlerProcess.pid, "SIGTERM");
      } catch {
        crawlerProcess.kill("SIGTERM");
      }
    }

    mainWindow?.webContents.send("crawl-progress", "🛑 Crawl stopped by user");

    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
});

// Fallback handler for unknown channels (debugging)
ipcMain.on("unknown-channel", async (event, { channel, data }) => {
  console.error(`[IPC] Unknown channel: ${channel}`);
});

// ==================== WINDOW MANAGEMENT ====================

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    title: "Anime Script AI",
    icon: path.join(UI_DIR, "public", "favicon.ico"),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true, // Changed from false to enable preload script
      preload: path.join(__dirname, "preload.js"), // Explicitly load preload
    },
  });

  // Load UI - in production load built files, in development load dev server
  const isDev = true;

  if (isDev) {
    mainWindow.loadURL("http://localhost:3000");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(
      path.join(UI_DIR, "build", "index.html"),
    );
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

// ==================== APP LIFECYCLE ====================

app.whenReady().then(() => {
  setupIPC();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  // Stop services on quit
  if (apiProcess) {
    apiProcess.kill();
  }

  app.quit();
});
