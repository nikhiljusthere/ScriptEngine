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
      setServiceStatus(result.services || {});
      setIsRunning(Object.values(result.services || {}).some(s => s === 'ok'));
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
            Services Status
          </Typography>
          <Grid container spacing={2}>
            {[
              { name: 'API Server', key: 'api' },
              { name: 'PostgreSQL', key: 'postgres' },
              { name: 'Qdrant', key: 'qdrant' },
              { name: 'Neo4j', key: 'neo4j' },
              { name: 'Elasticsearch', key: 'elasticsearch' },
              { name: 'Redis', key: 'redis' },
            ].map((service) => (
              <Grid item xs={12} sm={6} md={4} lg={2} key={service.key}>
                <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="body2" gutterBottom>
                    {service.name}
                  </Typography>
                  <Chip
                    icon={
                      serviceStatus[service.key] === 'ok' ? (
                        <CheckCircleOutline fontSize="small" color="success" />
                      ) : (
                        <ErrorOutline fontSize="small" color="error" />
                      )
                    }
                    label={serviceStatus[service.key] || 'stopped'}
                    size="small"
                    color={serviceStatus[service.key] === 'ok' ? 'success' : 'default'}
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
            { label: 'Architecture', value: 'Hybrid RAG + KG + LangGraph' },
            { label: 'LLM', value: 'Qwen2.5-72B (Local)' },
            { label: 'Embeddings', value: 'BGE-M3 (8192 context)' },
            { label: 'Vector DB', value: 'Qdrant' },
            { label: 'Knowledge Graph', value: 'Neo4j' },
            { label: 'Search', value: 'Elasticsearch 8 + BM25' },
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
