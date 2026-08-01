import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Grid,
  Alert,
  LinearProgress,
  IconButton,
  MenuItem,
} from "@mui/material";

import { ArrowBackOutlined, CloudUploadOutlined } from "@mui/icons-material";

const IngestionPage = () => {
  const navigate = useNavigate();

  const [series, setSeries] = useState("");
  const [url, setUrl] = useState(
    "",
  );
  const [outputFormat, setOutputFormat] = useState("txt");
  const [status, setStatus] = useState("idle");
  const [logs, setLogs] = useState([]);
  const [isCrawling, setIsCrawling] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [seriesExists, setSeriesExists] = useState(false);
  const [existingFiles, setExistingFiles] = useState(0);

  const [stats, setStats] = useState({
    links: 0,
    queue: 0,
    seen: 0,
  });

  const terminalRef = useRef(null);
  const crawlInFlightRef = useRef(false);

  useEffect(() => {
    if (!window.electron?.onCrawlProgress) {
      return;
    }

    const unsubscribe = window.electron.onCrawlProgress((msg) => {
      const match = msg.match(
        /\+(\d+)\s+links\s+\|\s+queue=(\d+)\s+\|\s+seen=(\d+)/i,
      );

      if (match) {
        setStats({
          links: Number(match[1]),
          queue: Number(match[2]),
          seen: Number(match[3]),
        });
      }

      const lines = msg.split("\n").filter((line) => line.trim());

      setLogs((prev) => {
        const updated = [...prev, ...lines];
        return updated.slice(-50);
      });
    });

    return () => {
      if (typeof unsubscribe === "function") {
        unsubscribe();
      } else {
        window.electron.removeCrawlProgressListeners?.();
      }
    };
  }, []);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const handleCrawl = async () => {
    if (crawlInFlightRef.current) {
      return;
    }

    crawlInFlightRef.current = true;
    setStatus("loading");
    setIsCrawling(true);

    setStats({
      links: 0,
      queue: 0,
      seen: 0,
    });

    setLogs([`🚀 Starting crawl for "${series}"...`]);

    try {
      const result = await window.electron.crawlSeries({
        series: series.trim(),
        url: url.trim(),
        output_format: outputFormat,
      });
      console.log(result.output);

      if (result?.running) {
        setStatus("loading");
        setLogs((prev) =>
          [
            ...prev,
            `⚠️ ${result.message || "A crawl is already running."}`,
          ].slice(-50),
        );
        return;
      }

      if (result?.stopped) {
        setStatus("idle");
        setIsCrawling(false);
        return;
      }

      setStatus("success");
      setIsCrawling(false);

      setLogs((prev) =>
        [...prev, "✅ Crawl completed successfully"].slice(-50),
      );

      console.log(result);
    } catch (error) {
      console.error(error);

      setStatus("error");
      setIsCrawling(false);

      setLogs((prev) =>
        [...prev, `❌ Error: ${error.message || "Unknown error"}`].slice(-50),
      );
    } finally {
      crawlInFlightRef.current = false;
    }
  };

  const handleStop = async () => {
    try {
      await window.electron.stopCrawl();

      setStatus("idle");
      setIsCrawling(false);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
        <IconButton onClick={() => navigate("/")} sx={{ mr: 2 }}>
          <ArrowBackOutlined />
        </IconButton>

        <Typography variant="h5">Crawl Anime Series</Typography>
      </Box>

      {status !== "idle" && (
        <Alert
          severity={
            status === "success"
              ? "success"
              : status === "error"
                ? "error"
                : "info"
          }
          sx={{ mb: 3 }}
        >
          {status === "loading" && (
            <>
              <LinearProgress sx={{ mb: 2 }} />

              <Box
                sx={{
                  display: "flex",
                  gap: 2,
                  flexWrap: "wrap",
                }}
              >
                <Box
                  sx={{
                    minWidth: 160,
                    fontFamily: "monospace",
                    fontWeight: 600,
                  }}
                >
                  Pages Seen: {stats.seen}
                </Box>
                <Box
                  sx={{
                    minWidth: 165,
                    fontFamily: "monospace",
                    fontWeight: 600,
                  }}
                >
                  Links Found: +{stats.links}
                </Box>
                <Box
                  sx={{
                    minWidth: 160,
                    fontFamily: "monospace",
                    fontWeight: 600,
                  }}
                >
                  Pages inQueue: {stats.queue}
                </Box>
              </Box>
            </>
          )}
        </Alert>
      )}

      <Paper elevation={2} sx={{ p: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Series Name"
              value={series}
              onChange={async (e) => {
                const value = e.target.value;
                setSeries(value);

                if (!value?.trim()) {
                  setSeriesExists(false);
                  return;
                }

                const result = await window.electron.checkSeriesExists(value);

                setSeriesExists(result.exists);
                setExistingFiles(result.fileCount || 0);
              }}
              placeholder="e.g., Naruto, One Piece"
            />
            {seriesExists && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                Name already exists. Found {existingFiles} Scrapped pages.
              </Alert>
            )}
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Start URL"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/anime/naruto"
              helperText="Enter the main wiki or series page URL"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              select
              fullWidth
              label="Save Format"
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value)}
            >
              <MenuItem value="txt">Text (.txt)</MenuItem>
              <MenuItem value="raw">Raw HTML (.html)</MenuItem>
            </TextField>
          </Grid>
          {series.trim() && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Output Directory"
                value={`out/step_one_raw_scrapped_data/${series || ""}`}
                disabled
              />
            </Grid>
          )}

          <Grid item xs={12}>
            <Box sx={{ display: "flex", gap: 2 }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleCrawl}
                disabled={
                  isCrawling || seriesExists || !series.trim() || !url.trim()
                }
                startIcon={<CloudUploadOutlined />}
              >
                Start Crawling
              </Button>

              <Button
                variant="outlined"
                color="error"
                size="large"
                onClick={handleStop}
                disabled={!isCrawling}
              >
                Stop Crawl
              </Button>

              <Button
                variant="outlined"
                size="large"
                onClick={() => setShowLogs((prev) => !prev)}
                disabled={!isCrawling}
              >
                Show Logs
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {showLogs && logs.length > 0 && (
        <Paper elevation={2} sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Crawl Logs (Last 50 Lines)
          </Typography>

          <Box
            ref={terminalRef}
            sx={{
              backgroundColor: "#000",
              color: "#00ff00",
              fontFamily: "Consolas, monospace",
              fontSize: 13,
              p: 2,
              height: 500,
              overflowY: "auto",
              whiteSpace: "pre-wrap",
              borderRadius: 1,
              border: "1px solid #333",
            }}
          >
            {logs.join("\n")}
          </Box>
        </Paper>
      )}
    </Container>
  );
};

export default IngestionPage;
