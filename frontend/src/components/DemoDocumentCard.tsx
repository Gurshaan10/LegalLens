import { Paper, Text, Group, Button, Stack, Badge, useMantineTheme, rem } from '@mantine/core';
import { IconFileText, IconSparkles } from '@tabler/icons-react';

interface DemoDocumentCardProps {
  onSelectDemo: () => void;
}

export default function DemoDocumentCard({ onSelectDemo }: DemoDocumentCardProps) {
  const theme = useMantineTheme();

  return (
    <Paper
      p="xl"
      radius="md"
      withBorder
      bg="dark.7"
      style={{
        borderColor: theme.colors.bronze[3],
        boxShadow: `0 0 ${rem(20)} rgba(171, 128, 73, 0.15)`,
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: `0 ${rem(5)} ${rem(25)} rgba(171, 128, 73, 0.25)`,
        }
      }}
      onClick={onSelectDemo}
    >
      <Stack gap="md">
        <Group justify="space-between">
          <Group>
            <IconFileText size={32} color={theme.colors.bronze[4]} />
            <div>
              <Text size="lg" fw={600} c="bronze.3">
                Demo Document
              </Text>
              <Text size="sm" c="bronze.5">
                Robinhood Cash Sweep Program
              </Text>
            </div>
          </Group>
          <Badge
            color="bronze"
            variant="light"
            size="lg"
            leftSection={<IconSparkles size={14} />}
          >
            Try Now
          </Badge>
        </Group>

        <Text size="sm" c="dark.1" mb="xs">
          Explore Legal Lens with our pre-loaded Robinhood High-Yield Cash Program agreement. This document covers cash sweep services, FDIC insurance, and interest-bearing deposit accounts.
        </Text>

        <Text size="xs" c="bronze.5" fw={600} mb={5}>
          Try asking:
        </Text>
        <Stack gap={4} mb="sm">
          <Text size="xs" c="dark.1">• "What is the FDIC insurance limit?"</Text>
          <Text size="xs" c="dark.1">• "How does the Cash Sweep Program work?"</Text>
          <Text size="xs" c="dark.1">• "What is the Brokerage-Held Cash Program threshold?"</Text>
          <Text size="xs" c="dark.1">• "How is interest calculated on deposits?"</Text>
        </Stack>

        <Group gap="xs">
          <Badge color="bronze" variant="dot">Unlimited Queries</Badge>
          <Badge color="bronze" variant="dot">No Sign-up Required</Badge>
          <Badge color="bronze" variant="dot">Instant Access</Badge>
        </Group>

        <Button
          fullWidth
          color="bronze"
          variant="light"
          size="md"
          leftSection={<IconSparkles size={18} />}
        >
          Query Demo Document
        </Button>
      </Stack>
    </Paper>
  );
}
