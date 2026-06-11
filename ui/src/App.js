import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Pages
import DashboardPage from './pages/DashboardPage';
import IngestionPage from './pages/IngestionPage';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6C5CE7',
    },
    secondary: {
      main: '#00CEC9',
    },
    background: {
      default: '#1A1A2E',
      paper: '#16213E',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/ingestion" element={<IngestionPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
