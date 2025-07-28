import { Container, Title, Text, Stack, Button, Group } from '@mantine/core';
import { useNavigate } from 'react-router-dom';

export default function AboutPage() {
  const navigate = useNavigate();

  return (
    <Container size="lg" py={100}>
      <Stack align="center" gap="xl">
        <Title order={1} size="3rem" c="bronze.3" ta="center">
          About Legal Lens
        </Title>
        
        <Text size="xl" c="bronze.4" ta="center" maw={800}>
          Legal Lens is an advanced document analysis tool that helps legal professionals and businesses understand complex legal documents with the power of AI.
        </Text>

        <Stack gap="md" maw={700}>
          <Text c="bronze.5">
            Our platform uses state-of-the-art natural language processing to:
          </Text>
          <ul style={{ color: 'var(--mantine-color-bronze-5)' }}>
            <li>Analyze legal documents for potential risks and opportunities</li>
            <li>Summarize complex legal language into clear, actionable insights</li>
            <li>Answer questions about your documents in plain English</li>
            <li>Identify key clauses and their implications</li>
          </ul>
        </Stack>

        <Group>
          <Button
            variant="filled"
            color="bronze"
            size="lg"
            onClick={() => navigate('/login')}
          >
            Try It Now
          </Button>
          <Button
            variant="outline"
            color="bronze"
            size="lg"
            onClick={() => navigate('/')}
          >
            Back to Home
          </Button>
        </Group>
      </Stack>
    </Container>
  );
} 