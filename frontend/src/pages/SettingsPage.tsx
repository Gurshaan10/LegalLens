import { Container, Title, Text, Paper, Stack, Switch, Group } from '@mantine/core';

export default function SettingsPage() {
  return (
    <Container size="lg" py="xl">
      <Paper p="xl" radius="md" withBorder bg="dark.7">
        <Stack>
          <Title order={2} c="bronze.3">Settings</Title>
          <Text c="bronze.5" mb="xl">
            Configure your Legal Lens experience
          </Text>
          
          <Group justify="space-between">
            <div>
              <Text fw={500} c="bronze.3">Dark Mode</Text>
              <Text size="sm" c="bronze.5">
                Toggle between light and dark theme
              </Text>
            </div>
            <Switch 
              checked={true}
              disabled
              color="bronze"
            />
          </Group>

          <Group justify="space-between">
            <div>
              <Text fw={500} c="bronze.3">Notifications</Text>
              <Text size="sm" c="bronze.5">
                Enable or disable notifications
              </Text>
            </div>
            <Switch 
              defaultChecked
              disabled
              color="bronze"
            />
          </Group>
        </Stack>
      </Paper>
    </Container>
  );
} 