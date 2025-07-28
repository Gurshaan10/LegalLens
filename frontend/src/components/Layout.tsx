import { AppShell, Group, Title, Text, rem, NavLink } from '@mantine/core';
import { IconHome, IconFileAnalytics, IconHistory } from '@tabler/icons-react';
import { Link, useLocation } from 'react-router-dom';

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  const navItems = [
    { icon: IconHome, label: 'Home', to: '/' },
    { icon: IconFileAnalytics, label: 'Document Analysis', to: '/app/analysis' },
    { icon: IconHistory, label: 'History', to: '/app/history' },
  ];

  return (
    <AppShell
      header={{ height: 70 }}
      navbar={{ width: 300, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Title order={1} size="h2" c="bronze.3">
              Legal Lens
            </Title>
            <Text c="bronze.5" size="sm" style={{ marginTop: rem(4) }}>
              Document Intelligence
            </Text>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md" bg="dark.7">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            component={Link}
            to={item.to}
            label={item.label}
            leftSection={<item.icon size={20} stroke={1.5} />}
            active={location.pathname === item.to}
            variant="filled"
            color="bronze"
            style={{ marginBottom: '0.5rem' }}
          />
        ))}
      </AppShell.Navbar>

      <AppShell.Main bg="dark.8">
        {children}
      </AppShell.Main>
    </AppShell>
  );
} 