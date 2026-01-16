import { useState, useEffect } from 'react';
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
  Collapse,
  Badge,
} from '@mantine/core';
import { IconSend, IconRefresh, IconFileText, IconChevronDown, IconChevronUp, IconEye } from '@tabler/icons-react';
import { useAuth } from '../contexts/AuthContext';
import apiEndpoints from '../config/api';
import type { DocumentInfo, QueryResponse } from '../types/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  documentId: string;
  onReset: () => void;
  isGuest?: boolean;
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

export default function ChatInterface({ documentId, onReset, isGuest = false }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [documentInfo, setDocumentInfo] = useState<DocumentInfo | null>(null);
  const [showDocInfo, setShowDocInfo] = useState(false);
  const theme = useMantineTheme();
  const { getIdToken, user } = useAuth();

  // Fetch document information on mount
  useEffect(() => {
    const fetchDocumentInfo = async () => {
      try {
        const response = await fetch(apiEndpoints.documentInfo(documentId));
        if (response.ok) {
          const data = await response.json();
          setDocumentInfo(data);
        }
      } catch (error) {
        console.error('Failed to fetch document info:', error);
      }
    };
    fetchDocumentInfo();
  }, [documentId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Check for multiple questions (numbered lists like "1.", "2." only)
    // Allow multiple ? marks in a single question (like "Really???" or "Is this safe???")
    const trimmedInput = input.trim();
    const hasNumberedList = /^\d+\.|["']\d+\.|[.!]\s*\d+\./m.test(trimmedInput);

    // Check for multiple distinct questions by looking for ? followed by non-? content and another ?
    // This allows "Really???" but catches "What is X? What is Y?"
    const hasMultipleQuestions = /\?\s*[^?]+\?/.test(trimmedInput);

    if (hasNumberedList || hasMultipleQuestions) {
      setMessages((prev) => [
        ...prev,
        { role: 'user' as const, content: trimmedInput },
        {
          role: 'assistant',
          content: '⚠️ **Please ask one question at a time for better accuracy.**\n\nI noticed you asked multiple questions. For the best results, please:\n\n• Ask one specific question per query\n• Wait for my response\n• Then ask your next question\n\nThis helps me provide more accurate and detailed answers for each question.',
        },
      ]);
      setInput('');
      return;
    }

    const userMessage = { role: 'user' as const, content: trimmedInput };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Add authorization header only if user is authenticated
      if (!isGuest && user) {
        const idToken = await getIdToken();
        if (idToken) {
          headers['Authorization'] = `Bearer ${idToken}`;
        }
      }

      const response = await fetch(apiEndpoints.query(documentId), {
        method: 'POST',
        headers,
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
      {/* Document Header */}
      <Stack gap="xs" mb="md">
        <Group justify="space-between">
          <Group>
            <IconFileText size={24} color={theme.colors.bronze[4]} />
            <div>
              <Text size="lg" fw={500} c="bronze.3">
                {documentInfo?.filename || 'Document Analysis'}
              </Text>
              {documentInfo?.is_demo && (
                <Badge color="bronze" variant="dot" size="sm">Demo Document</Badge>
              )}
            </div>
          </Group>
          <Group>
            {documentInfo?.can_view && (
              <ActionIcon
                variant="filled"
                color="bronze"
                onClick={() => window.open(apiEndpoints.documentView(documentId), '_blank')}
                title="View PDF document"
              >
                <IconEye size={18} />
              </ActionIcon>
            )}
            <ActionIcon
              variant="subtle"
              color="bronze"
              onClick={() => setShowDocInfo(!showDocInfo)}
              title="View document details"
            >
              {showDocInfo ? <IconChevronUp size={18} /> : <IconChevronDown size={18} />}
            </ActionIcon>
            <ActionIcon
              variant="light"
              color="bronze"
              onClick={onReset}
              title="Upload new document"
            >
              <IconRefresh size={20} />
            </ActionIcon>
          </Group>
        </Group>

        {/* Collapsible Document Info */}
        <Collapse in={showDocInfo}>
          <Paper p="sm" bg="dark.8" radius="sm">
            <Stack gap="xs">
              <Group gap="xl">
                <div>
                  <Text size="xs" c="bronze.5" fw={500}>Document Chunks</Text>
                  <Text size="sm" c="dark.0">{documentInfo?.chunks || 0}</Text>
                </div>
                <div>
                  <Text size="xs" c="bronze.5" fw={500}>Text Length</Text>
                  <Text size="sm" c="dark.0">
                    {documentInfo?.text_length?.toLocaleString() || 0} characters
                  </Text>
                </div>
              </Group>
              <Text size="xs" c="dark.2">
                This document has been processed and is ready for analysis. Ask any questions about its content.
              </Text>
              {documentInfo?.can_view && (
                <Button
                  size="xs"
                  variant="light"
                  color="bronze"
                  leftSection={<IconEye size={14} />}
                  onClick={() => window.open(apiEndpoints.documentView(documentId), '_blank')}
                  fullWidth
                >
                  View Full PDF Document
                </Button>
              )}
            </Stack>
          </Paper>
        </Collapse>
      </Stack>

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