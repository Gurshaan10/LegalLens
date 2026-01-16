import { AppShell, Group, Title, Text, rem, NavLink, Menu, Button, Badge } from '@mantine/core';
import { IconFileAnalytics, IconHistory, IconUser, IconLogout, IconCoins } from '@tabler/icons-react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { auth } from '../firebase';
import { signOut } from 'firebase/auth';
import { useState, useEffect } from 'react';
import { apiEndpoints } from '../config/api';
import type { UserProfile } from '../types/api';

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const { user, getIdToken } = useAuth();
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  const navItems = [
    { icon: IconFileAnalytics, label: 'Document Analysis', to: user ? '/analysis' : '/' },
    { icon: IconHistory, label: 'History', to: '/app/history' },
  ];

  useEffect(() => {
    const fetchUserProfile = async () => {
      if (user) {
        try {
          const token = await getIdToken();
          const response = await fetch(apiEndpoints.me, {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
          });
          if (response.ok) {
            const data: UserProfile = await response.json();
            setUserProfile(data);
          }
        } catch (error) {
          console.error('Error fetching user profile:', error);
        }
      }
    };

    fetchUserProfile();
    const interval = setInterval(fetchUserProfile, 5000);
    return () => clearInterval(interval);
  }, [user, getIdToken]);

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      window.location.href = '/';
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

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

          {user && (
            <Menu shadow="md" width={250}>
              <Menu.Target>
                <Button
                  variant="light"
                  color="bronze"
                  leftSection={<IconUser size={18} />}
                  rightSection={
                    userProfile && (
                      <Badge color="bronze" variant="filled" size="sm">
                        {userProfile.credits} credits
                      </Badge>
                    )
                  }
                >
                  {user.email?.split('@')[0] || 'Account'}
                </Button>
              </Menu.Target>

              <Menu.Dropdown>
                <Menu.Label>Account</Menu.Label>
                <Menu.Item leftSection={<IconUser size={16} />}>
                  <Text size="sm" fw={500}>{user.email}</Text>
                </Menu.Item>

                {userProfile && (
                  <Menu.Item leftSection={<IconCoins size={16} />}>
                    <Text size="sm">Credits: {userProfile.credits}</Text>
                  </Menu.Item>
                )}

                <Menu.Divider />

                <Menu.Item
                  color="red"
                  leftSection={<IconLogout size={16} />}
                  onClick={handleSignOut}
                >
                  Sign Out
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          )}
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