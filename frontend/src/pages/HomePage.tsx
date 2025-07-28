import { Container, Title, Text, Paper, Button, Group, rem } from '@mantine/core';
import { IconFileUpload, IconHistory } from '@tabler/icons-react';
import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <Container size="lg" py="xl">
      <Title order={1} size="h1" mb="xl" c="bronze.3" ta="center">
        Welcome to Legal Lens
      </Title>
      <Text size="lg" c="bronze.4" mb={50} ta="center">
        Analyze legal documents with AI-powered intelligence
      </Text>

      <Group justify="center" gap="xl">
        <Paper
          p="xl"
          radius="md"
          withBorder
          bg="dark.7"
          style={{
            width: '300px',
            borderColor: 'var(--mantine-color-bronze-3)',
            boxShadow: `0 0 ${rem(20)} rgba(171, 128, 73, 0.1)`
          }}
        >
          <IconFileUpload size={48} style={{ color: 'var(--mantine-color-bronze-4)' }} />
          <Title order={3} mt="md" mb="xs" c="bronze.3">
            Analyze Document
          </Title>
          <Text c="dark.0" mb="xl">
            Upload and analyze legal documents using our AI-powered system.
          </Text>
          <Button
            component={Link}
            to="/analysis"
            variant="filled"
            color="bronze"
            fullWidth
          >
            Start Analysis
          </Button>
        </Paper>

        <Paper
          p="xl"
          radius="md"
          withBorder
          bg="dark.7"
          style={{
            width: '300px',
            borderColor: 'var(--mantine-color-bronze-3)',
            boxShadow: `0 0 ${rem(20)} rgba(171, 128, 73, 0.1)`
          }}
        >
          <IconHistory size={48} style={{ color: 'var(--mantine-color-bronze-4)' }} />
          <Title order={3} mt="md" mb="xs" c="bronze.3">
            View History
          </Title>
          <Text c="dark.0" mb="xl">
            Access your previously analyzed documents and conversations.
          </Text>
          <Button
            component={Link}
            to="/history"
            variant="filled"
            color="bronze"
            fullWidth
          >
            View History
          </Button>
        </Paper>
      </Group>
    </Container>
  );
} 