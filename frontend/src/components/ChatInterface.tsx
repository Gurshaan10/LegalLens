import { useState } from 'react';
import {
  Paper,
  TextInput,
  Button,
  Stack,
  Group,
  Text,
  ScrollArea,
  ActionIcon,
  useMantineTheme,
  rem,
  Box,
} from '@mantine/core';
import { IconSend, IconRefresh } from '@tabler/icons-react';
import { useAuth } from '../contexts/AuthContext';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  documentId: string;
  onReset: () => void;
}

// Function to format text with proper line breaks and styling
const formatMessage = (content: string) => {
  // Split by double line breaks to create paragraphs
  const paragraphs = content.split('\n\n');
  
  return paragraphs.map((paragraph, index) => {
    // Handle bullet points
    if (paragraph.trim().startsWith('•')) {
      const items = paragraph.split('\n').filter(line => line.trim().startsWith('•'));
      return (
        <Box key={index} mb="xs">
          {items.map((item, itemIndex) => (
            <Text key={itemIndex} size="sm" c="dark.0" style={{ marginLeft: '1rem' }}>
              {item}
            </Text>
          ))}
        </Box>
      );
    }
    
    // Handle numbered lists
    if (paragraph.trim().match(/^\d+\./)) {
      const items = paragraph.split('\n').filter(line => line.trim().match(/^\d+\./));
      return (
        <Box key={index} mb="xs">
          {items.map((item, itemIndex) => (
            <Text key={itemIndex} size="sm" c="dark.0" style={{ marginLeft: '1rem' }}>
              {item}
            </Text>
          ))}
        </Box>
      );
    }
    
    // Handle bold text (simple **text** format)
    const formattedText = paragraph.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Handle single line breaks
    const lines = formattedText.split('\n');
    return (
      <Box key={index} mb="xs">
        {lines.map((line, lineIndex) => (
          <Text 
            key={lineIndex} 
            size="sm" 
            c="dark.0" 
            dangerouslySetInnerHTML={{ __html: line }}
            style={{ marginBottom: lineIndex < lines.length - 1 ? '0.5rem' : '0' }}
          />
        ))}
      </Box>
    );
  });
};

export default function ChatInterface({ documentId, onReset }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const theme = useMantineTheme();
  const { getIdToken } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user' as const, content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const idToken = await getIdToken();
      if (!idToken) throw new Error('Not authenticated');
      const response = await fetch(`http://localhost:8000/query/${documentId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify({
          query: userMessage.content
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      const assistantMessage = {
        role: 'assistant' as const,
        content: data.answer,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error while processing your request.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Paper 
      p="md" 
      radius="md" 
      withBorder 
      bg="dark.7"
      style={{
        borderColor: theme.colors.bronze[3],
        boxShadow: `0 0 ${rem(20)} rgba(171, 128, 73, 0.1)`,
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 180px)'
      }}
    >
      <Group justify="space-between" mb="md">
        <Text size="lg" fw={500} c="bronze.3">
          Chat with your Document
        </Text>
        <ActionIcon
          variant="light"
          color="bronze"
          onClick={onReset}
          title="Upload new document"
        >
          <IconRefresh size={20} />
        </ActionIcon>
      </Group>

      <ScrollArea 
        flex={1} 
        mb="md"
        style={{
          backgroundColor: theme.colors.dark[8],
          borderRadius: theme.radius.sm,
          padding: rem(10)
        }}
      >
        <Stack gap="md">
          {messages.map((message, index) => (
            <Paper
              key={index}
              p="sm"
              radius="md"
              bg={message.role === 'user' ? 'bronze.8' : 'dark.6'}
              style={{
                alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%',
                borderLeft: message.role === 'assistant' ? `4px solid ${theme.colors.bronze[4]}` : 'none',
                borderRight: message.role === 'user' ? `4px solid ${theme.colors.bronze[4]}` : 'none',
              }}
            >
              {message.role === 'user' ? (
                <Text size="sm" c="bronze.1">
                  {message.content}
                </Text>
              ) : (
                <Box>
                  {formatMessage(message.content)}
                </Box>
              )}
            </Paper>
          ))}
        </Stack>
      </ScrollArea>

      <form onSubmit={handleSubmit}>
        <Group gap="sm">
          <TextInput
            placeholder="Ask a question about your document..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={{ flex: 1 }}
            disabled={isLoading}
            styles={{
              input: {
                backgroundColor: theme.colors.dark[6],
                borderColor: theme.colors.bronze[3],
                color: theme.colors.dark[0],
                '&:focus': {
                  borderColor: theme.colors.bronze[5]
                }
              }
            }}
          />
          <Button 
            type="submit" 
            loading={isLoading}
            color="bronze"
            variant="filled"
          >
            <IconSend size={20} />
          </Button>
        </Group>
      </form>
    </Paper>
  );
} 