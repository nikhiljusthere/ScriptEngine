import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  RocketLaunchOutlined,
  CloudUploadOutlined,
  AutoAwesomeOutlined,
  SearchOutlined,
  PlayCircleOutline,
  StopCircleOutlined,
  CheckCircleOutline,
  ErrorOutline,
  InfoOutlined,
} from '@mui/icons-material';

const DashboardPage = () => {
  const navigate = useNavigate();
  const [serviceStatus, setServiceStatus] = useState({});
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    checkHealth();
    
    // Poll health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const result = await window.electron.ipcRenderer.invoke('health-check');
      // /health reports the API itself, the resolved torch device and the
      // indexed series. It has no `services` key — there are no services. The
      // stores are files, so "running" means the API answered.
      setServiceStatus(result);
      setIsRunning(result.status === 'ok');
    } catch (error) {
      // Service not available
    }
  };

  const handleStartServices = async () => {
    try {
      await window.electron.ipcRenderer.invoke('start-services');
      setIsRunning(true);
    } catch (error) {
      console.error('Failed to start services:', error);
    }
  };

  const handleStopServices = async () => {
    try {
      await window.electron.ipcRenderer.invoke('stop-services');
      setIsRunning(false);
    } catch (error) {
      console.error('Failed to stop services:', error);
    }
  };

  const navItems = [
    {
      title: 'Ingest Content',
      description: 'Crawl websites or upload documents for processing',
      icon: <CloudUploadOutlined sx={{ fontSize: 40 }} />,
      path: '/ingestion',
      color: '#6C5CE7',
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">Dashboard</Typography>
        
        <Box>
          {isRunning ? (
            <Tooltip title="Stop all services">
              <IconButton onClick={handleStopServices} color="error">
                <StopCircleOutlined />
              </IconButton>
            </Tooltip>
          ) : (
            <Tooltip title="Start services">
              <IconButton onClick={handleStartServices} color="success">
                <PlayCircleOutline />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </Box>

      {/* Service Status */}
      {isRunning && (
        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Engine Status
          </Typography>
          <Grid container spacing={2}>
            {[
              { name: 'API Server', value: serviceStatus.status },
              { name: 'Device', value: serviceStatus.device },
              { name: 'Version', value: serviceStatus.version },
              {
                name: 'Series Indexed',
                value: (serviceStatus.series || []).join(', '),
              },
            ].map((service) => (
              <Grid item xs={12} sm={6} md={3} key={service.name}>
                <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="body2" gutterBottom>
                    {service.name}
                  </Typography>
                  <Chip
                    icon={
                      service.value ? (
                        <CheckCircleOutline fontSize="small" color="success" />
                      ) : (
                        <ErrorOutline fontSize="small" color="error" />
                      )
                    }
                    label={service.value || 'unavailable'}
                    size="small"
                    color={service.value ? 'success' : 'default'}
                    sx={{ mt: 1 }}
                  />
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Main Navigation */}
      <Grid container spacing={3}>
        {navItems.map((item, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6,
                },
              }}
            >
              <CardContent sx={{ flex: 1 }}>
                <Box sx={{ color: item.color, mb: 2 }}>
                  {item.icon}
                </Box>
                <Typography variant="h5" component="h2" gutterBottom>
                  {item.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {item.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  size="large" 
                  fullWidth
                  variant="contained"
                  onClick={() => navigate(item.path)}
                  sx={{ bgcolor: item.color, '&:hover': { bgcolor: item.color } }}
                >
                  Open
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quick Stats */}
      <Paper elevation={2} sx={{ p: 3, mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          System Information
        </Typography>
        <Grid container spacing={2}>
          {[
            { label: 'Architecture', value: 'Wikitext ingestion + hybrid retrieval' },
            { label: 'Embeddings', value: serviceStatus.embed_model || 'BAAI/bge-large-en-v1.5' },
            { label: 'Reranker', value: serviceStatus.rerank_model || 'BAAI/bge-reranker-v2-m3' },
            { label: 'Vector Store', value: 'Qdrant (embedded)' },
            { label: 'Facts / Graph / BM25', value: 'SQLite + FTS5' },
            { label: 'Generation', value: 'Downstream, in ComfyUI' },
          ].map((stat, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Typography variant="body2" color="text.secondary">
                {stat.label}:
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {stat.value}
              </Typography>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Container>
  );
};

export default DashboardPage;
