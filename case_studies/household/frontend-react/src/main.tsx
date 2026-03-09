import React from 'react';
import ReactDOM from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import '@mantine/core/styles.css';
import './index.css';

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MantineProvider defaultColorScheme="light">
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </MantineProvider>
  </React.StrictMode>
);
