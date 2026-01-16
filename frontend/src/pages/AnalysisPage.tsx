import { useState, useEffect } from 'react';
import { Container, Loader, Group, Text, Badge, Stack, Title, Grid, Paper, Button } from '@mantine/core';
import { IconLogin } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import DocumentUpload from '../components/DocumentUpload';
import ChatInterface from '../components/ChatInterface';
import DemoDocumentCard from '../components/DemoDocumentCard';
import { useAuth } from '../contexts/AuthContext';
import apiEndpoints from '../config/api';
import type { UserProfile } from '../types/api';

const DEMO_DOCUMENT_ID = 'demo-robinhood-document';

export default function AnalysisPage() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [credits, setCredits] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [isGuest, setIsGuest] = useState(true);
  const { getIdToken, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCredits = async () => {
      // Only fetch credits if user is authenticated
      if (!user) {
        setIsGuest(true);
        setCredits(null);
        setLoading(false);
        return;
      }

      setIsGuest(false);
      setLoading(true);
      try {
        const idToken = await getIdToken();
        if (!idToken) throw new Error('Not authenticated');
        const response = await fetch(apiEndpoints.me, {
          headers: { Authorization: `Bearer ${idToken}` },
        });
        if (!response.ok) throw new Error('Failed to fetch user profile');
        const data: UserProfile = await response.json();
        setCredits(data.credits);
      } catch (error) {
        console.error('Failed to fetch credits:', error);
        setCredits(null);
      } finally {
        setLoading(false);
      }
    };
    fetchCredits();
  }, [documentId, getIdToken, user]);

  const handleDemoSelect = () => {
    setDocumentId(DEMO_DOCUMENT_ID);
  };

  const handleUploadSuccess = (docId: string) => {
    setDocumentId(docId);
  };

  const handleReset = () => {
    setDocumentId(null);
  };

  if (loading) {
    return (
      <Container size="lg" py="xl">
        <Group justify="center" align="center">
          <Loader color="bronze" />
        </Group>
      </Container>
    );
  }

  return (
    <Container size="lg" py="xl">
      {/* Header with Credits/Guest Info */}
      <Group justify="space-between" mb="xl">
        <div>
          <Title order={2} c="bronze.3">
            {documentId ? 'Document Analysis' : 'Get Started'}
          </Title>
          {isGuest && !documentId && (
            <Text size="sm" c="bronze.5" mt={5}>
              No sign-up required • Try the demo or upload your own document
            </Text>
          )}
        </div>
        <Group>
          {isGuest ? (
            <>
              <Badge color="bronze" variant="light" size="lg">
                Guest Mode
              </Badge>
              <Button
                size="sm"
                color="bronze"
                variant="light"
                leftSection={<IconLogin size={16} />}
                onClick={() => navigate('/login')}
              >
                Sign In for 5 Credits
              </Button>
            </>
          ) : (
            <Badge color={credits === 0 ? 'red' : 'bronze'} size="lg">
              Credits: {credits ?? '—'}
            </Badge>
          )}
        </Group>
      </Group>

      {!documentId ? (
        <Stack gap="xl">
          {/* Demo Document Section */}
          <div>
            <Title order={3} c="bronze.4" mb="md">
              Try the Demo
            </Title>
            <DemoDocumentCard onSelectDemo={handleDemoSelect} />
          </div>

          {/* Upload Your Own Section */}
          <div>
            <Title order={3} c="bronze.4" mb="md">
              {isGuest ? 'Upload Your Own (2 free per day)' : 'Upload Your Document'}
            </Title>
            <DocumentUpload
              onUploadSuccess={handleUploadSuccess}
              credits={credits ?? undefined}
              isGuest={isGuest}
            />
          </div>

          {/* Guest Info Banner */}
          {isGuest && (
            <Paper p="md" bg="bronze.9" radius="md" withBorder style={{ borderColor: '#AB8049' }}>
              <Text size="sm" c="bronze.3" ta="center">
                💡 <strong>Guest users</strong> get 2 free uploads per day. <strong>Sign in</strong> to get 5 credits and save your analysis history!
              </Text>
            </Paper>
          )}
        </Stack>
      ) : (
        <ChatInterface
          documentId={documentId}
          onReset={handleReset}
          isGuest={isGuest || documentId === DEMO_DOCUMENT_ID}
        />
      )}
    </Container>
  );
}
