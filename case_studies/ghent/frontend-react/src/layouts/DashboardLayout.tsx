import React from 'react';
import { AppShell, Group, Text, Burger, NavLink, Divider, ScrollArea, Box } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconLayoutDashboard, IconSettings } from '@tabler/icons-react';
import { Link, useLocation } from 'react-router-dom';
import EntityDetails from '../components/common/EntityDetails';

const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [opened, { toggle }] = useDisclosure();
    const location = useLocation();

    return (
        <AppShell
            header={{ height: 60 }}
            navbar={{
                width: 320,
                breakpoint: 'sm',
                collapsed: { mobile: !opened },
            }}
            padding="md"
        >
            <AppShell.Header p="md">
                <Group h="100%" px="md">
                    <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
                    <Text size="lg" fw={700}>
                        Ghent Water System
                    </Text>
                </Group>
            </AppShell.Header>

            <AppShell.Navbar p="0">
                <ScrollArea h="100%">
                    <Box p="md">
                        <NavLink
                            component={Link}
                            to="/"
                            label="Dashboard"
                            leftSection={<IconLayoutDashboard size={16} />}
                            active={location.pathname === '/'}
                        />
                        <NavLink
                            component={Link}
                            to="/settings"
                            label="Settings"
                            leftSection={<IconSettings size={16} />}
                            active={location.pathname === '/settings'}
                        />
                    </Box>

                    <Divider label="Entity Details" labelPosition="center" />
                    <EntityDetails />
                </ScrollArea>
            </AppShell.Navbar>

            <AppShell.Main>{children}</AppShell.Main>
        </AppShell>
    );
};

export default DashboardLayout;
