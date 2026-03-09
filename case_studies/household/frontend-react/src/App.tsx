import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell, Text, Group, ThemeIcon, UnstyledButton, Box, Stack } from '@mantine/core';
import { IconHome, IconFilter, IconDroplet, IconArrowsExchange } from '@tabler/icons-react';
import { useNavigate, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import MBRView from './pages/MBRView';
import ROView from './pages/ROView';
import InfiltrationView from './pages/InfiltrationView';

interface NavItemProps {
    icon: React.ElementType;
    label: string;
    path: string;
    color: string;
}

const NavItem: React.FC<NavItemProps> = ({ icon: Icon, label, path, color }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const isActive = location.pathname === path;

    return (
        <UnstyledButton
            onClick={() => navigate(path)}
            style={(theme) => ({
                display: 'block',
                width: '100%',
                padding: theme.spacing.xs,
                borderRadius: theme.radius.sm,
                color: isActive ? theme.colors[color][6] : theme.colors.gray[7],
                backgroundColor: isActive ? theme.colors[color][0] : 'transparent',
                '&:hover': {
                    backgroundColor: isActive ? theme.colors[color][1] : theme.colors.gray[0],
                },
            })}
        >
            <Group>
                <ThemeIcon color={color} variant={isActive ? 'filled' : 'light'} size="md">
                    <Icon size={18} />
                </ThemeIcon>
                <Text size="sm" fw={isActive ? 600 : 400}>{label}</Text>
            </Group>
        </UnstyledButton>
    );
};

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
        <AppShell
            header={{ height: 60 }}
            navbar={{ width: 250, breakpoint: 'sm' }}
            padding={0}
        >
            <AppShell.Header />
            <AppShell.Navbar p="xs">
                <AppShell.Section mb="md">
                    <Group justify="center" mb="lg" mt="sm">
                        <ThemeIcon size="xl" radius="xl" color="blue">
                            <IconHome size={28} />
                        </ThemeIcon>
                        <Box>
                            <Text fw={700} size="lg">Household</Text>
                            <Text size="xs" c="dimmed">Water System</Text>
                        </Box>
                    </Group>
                </AppShell.Section>

                <AppShell.Section grow>
                    <Stack gap="xs">
                        <NavItem icon={IconHome} label="Dashboard" path="/" color="blue" />
                        <NavItem icon={IconFilter} label="MBR System" path="/mbr" color="blue" />
                        <NavItem icon={IconDroplet} label="RO System" path="/ro" color="cyan" />
                        <NavItem icon={IconArrowsExchange} label="Infiltration" path="/infiltration" color="green" />
                    </Stack>
                </AppShell.Section>

                <AppShell.Section>
                    <Box p="xs" style={{ borderTop: '1px solid #eee' }}>
                        <Text size="xs" c="dimmed" ta="center">
                            Household Water System v1.0
                        </Text>
                    </Box>
                </AppShell.Section>
            </AppShell.Navbar>
            <AppShell.Main style={{ backgroundColor: '#f8f9fa' }}>
                {children}
            </AppShell.Main>
        </AppShell>
    );
};

const App: React.FC = () => {
    return (
        <BrowserRouter>
            <Layout>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/mbr" element={<MBRView />} />
                    <Route path="/ro" element={<ROView />} />
                    <Route path="/infiltration" element={<InfiltrationView />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </Layout>
        </BrowserRouter>
    );
};

export default App;