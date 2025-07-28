import { useState, useEffect } from 'react';
import { 
  Container, 
  Title, 
  Text, 
  Paper, 
  Stack, 
  Card, 
  Group, 
  Badge, 
  ActionIcon, 
  Modal,
  ScrollArea,
  Divider,
  useMantineTheme,
  rem
} from '@mantine/core';
import { IconEye, IconFile, IconCalendar, IconClock, IconMessage } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { useAuth } from '../contexts/AuthContext';

interface Document {
  id: string;
  filename: string;
  upload_date: string;
  file_size: number;
  text_length: number;
  processing_status: string;
  meta: any;
}

interface Query {
  id: string;
  query_text: string;
  response_text: string;
  query_date: string;
  response_time_ms: number;
}

interface HistoryData {
  documents: Document[];
  summary: {
    total_documents: number;
    total_size_bytes: number;
    recent_documents: Document[];
  };
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [documentQueries, setDocumentQueries] = useState<Query[]>([]);
  const [queriesModalOpen, setQueriesModalOpen] = useState(false);
  const theme = useMantineTheme();
  const { getIdToken } = useAuth();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const idToken = await getIdToken();
      if (!idToken) throw new Error('Not authenticated');
      const response = await fetch('http://localhost:8000/history/', {
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch history');
      }
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error('Error fetching history:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to load document history',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchDocumentQueries = async (documentId: string) => {
    try {
      const idToken = await getIdToken();
      if (!idToken) throw new Error('Not authenticated');
      const response = await fetch(`http://localhost:8000/history/${documentId}/queries`, {
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch document queries');
      }
      const data = await response.json();
      setDocumentQueries(data.queries);
    } catch (error) {
      console.error('Error fetching document queries:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to load document queries',
        color: 'red',
      });
    }
  };

  const handleViewQueries = async (document: Document) => {
    setSelectedDocument(document);
    await fetchDocumentQueries(document.id);
    setQueriesModalOpen(true);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  if (loading) {
    return (
      <Container size="lg" py="xl">
        <Paper p="xl" radius="md" withBorder bg="dark.7">
          <Stack align="center">
            <Title order={2} c="bronze.3">Document History</Title>
            <Text c="bronze.5">Loading your documents...</Text>
          </Stack>
        </Paper>
      </Container>
    );
  }

  return (
    <Container size="lg" py="xl">
      <Stack gap="xl">
        {/* Summary Section */}
        {history && (
          <Paper p="xl" radius="md" withBorder bg="dark.7">
            <Stack>
              <Title order={2} c="bronze.3">Document History</Title>
              <Group>
                <Badge color="bronze" variant="light" size="lg">
                  {history.summary.total_documents} Documents
                </Badge>
                <Badge color="bronze" variant="light" size="lg">
                  {formatFileSize(history.summary.total_size_bytes)} Total
                </Badge>
              </Group>
            </Stack>
          </Paper>
        )}

        {/* Documents List */}
        {history?.documents.length === 0 ? (
          <Paper p="xl" radius="md" withBorder bg="dark.7">
            <Stack align="center">
              <IconFile size={48} color={theme.colors.bronze[3]} />
              <Text c="bronze.5" ta="center">
                No documents found. Upload your first document to see it here.
              </Text>
            </Stack>
          </Paper>
        ) : (
          <Stack gap="md">
            {history?.documents.map((document) => (
              <Card 
                key={document.id} 
                p="md" 
                radius="md" 
                withBorder 
                bg="dark.7"
                style={{ borderColor: theme.colors.bronze[3] }}
              >
                <Group justify="space-between" align="flex-start">
                  <Stack gap="xs" style={{ flex: 1 }}>
                    <Group gap="sm">
                      <IconFile size={20} color={theme.colors.bronze[3]} />
                      <Text fw={500} c="bronze.1" size="lg">
                        {document.filename}
                      </Text>
                      <Badge 
                        color={document.processing_status === 'completed' ? 'green' : 'yellow'}
                        variant="light"
                      >
                        {document.processing_status}
                      </Badge>
                    </Group>
                    
                    <Group gap="lg" c="bronze.5" fs="sm">
                      <Group gap="xs">
                        <IconCalendar size={16} />
                        <Text>{formatDate(document.upload_date)}</Text>
                      </Group>
                      <Group gap="xs">
                        <IconFile size={16} />
                        <Text>{formatFileSize(document.file_size)}</Text>
                      </Group>
                      {document.text_length > 0 && (
                        <Group gap="xs">
                          <IconMessage size={16} />
                          <Text>{document.text_length.toLocaleString()} chars</Text>
                        </Group>
                      )}
                    </Group>

                    {document.meta && (
                      <Group gap="sm">
                        {document.meta.pages && (
                          <Badge size="xs" variant="outline" color="bronze">
                            {document.meta.pages} pages
                          </Badge>
                        )}
                        {document.meta.processing_method && (
                          <Badge size="xs" variant="outline" color="bronze">
                            {document.meta.processing_method}
                          </Badge>
                        )}
                      </Group>
                    )}
                  </Stack>

                  <ActionIcon
                    variant="light"
                    color="bronze"
                    onClick={() => handleViewQueries(document)}
                    title="View queries"
                  >
                    <IconEye size={20} />
                  </ActionIcon>
                </Group>
              </Card>
            ))}
          </Stack>
        )}
      </Stack>

      {/* Queries Modal */}
      <Modal
        opened={queriesModalOpen}
        onClose={() => setQueriesModalOpen(false)}
        title={
          <Group>
            <IconMessage size={20} />
            <Text>Document Queries</Text>
          </Group>
        }
        size="lg"
        styles={{
          title: { color: theme.colors.bronze[3] },
          header: { backgroundColor: theme.colors.dark[7] },
          body: { backgroundColor: theme.colors.dark[7] }
        }}
      >
        {selectedDocument && (
          <Stack gap="md">
            <Paper p="md" radius="md" bg="dark.6">
              <Text fw={500} c="bronze.1">{selectedDocument.filename}</Text>
              <Text size="sm" c="bronze.5">{formatDate(selectedDocument.upload_date)}</Text>
            </Paper>

            <Divider />

            {documentQueries.length === 0 ? (
              <Text c="bronze.5" ta="center" py="xl">
                No queries found for this document.
              </Text>
            ) : (
              <ScrollArea h={400}>
                <Stack gap="md">
                  {documentQueries.map((query) => (
                    <Card key={query.id} p="md" radius="md" bg="dark.6">
                      <Stack gap="sm">
                        <Group justify="space-between">
                          <Text fw={500} c="bronze.1" size="sm">Query</Text>
                          <Group gap="xs">
                            <IconClock size={14} />
                            <Text size="xs" c="bronze.5">
                              {query.response_time_ms}ms
                            </Text>
                          </Group>
                        </Group>
                        <Text size="sm" c="bronze.3">{query.query_text}</Text>
                        
                        <Divider size="xs" />
                        
                        <Text fw={500} c="bronze.1" size="sm">Response</Text>
                        <Text size="sm" c="bronze.3" style={{ whiteSpace: 'pre-wrap' }}>
                          {query.response_text}
                        </Text>
                        
                        <Text size="xs" c="bronze.5" ta="right">
                          {formatDate(query.query_date)}
                        </Text>
                      </Stack>
                    </Card>
                  ))}
                </Stack>
              </ScrollArea>
            )}
          </Stack>
        )}
      </Modal>
    </Container>
  );
} 