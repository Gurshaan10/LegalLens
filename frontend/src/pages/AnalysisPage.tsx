import { useState, useEffect } from 'react';
import { Container, Loader, Group, Text, Badge } from '@mantine/core';
import DocumentUpload from '../components/DocumentUpload';
import ChatInterface from '../components/ChatInterface';
import { useAuth } from '../contexts/AuthContext';

export default function AnalysisPage() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [credits, setCredits] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const { getIdToken } = useAuth();

  useEffect(() => {
    const fetchCredits = async () => {
      setLoading(true);
      try {
        const idToken = await getIdToken();
        if (!idToken) throw new Error('Not authenticated');
        const response = await fetch('http://localhost:8000/me', {
          headers: { Authorization: `Bearer ${idToken}` },
        });
        if (!response.ok) throw new Error('Failed to fetch user profile');
        const data = await response.json();
        setCredits(data.credits);
      } catch (error) {
        setCredits(null);
      } finally {
        setLoading(false);
      }
    };
    fetchCredits();
  }, [documentId, getIdToken]);

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
      <Group justify="end" mb="md">
        <Badge color={credits === 0 ? 'red' : 'bronze'} size="lg">
          Credits: {credits ?? '—'}
        </Badge>
      </Group>
      {!documentId ? (
        <DocumentUpload onUploadSuccess={setDocumentId} credits={credits ?? 0} />
      ) : (
        <ChatInterface documentId={documentId} onReset={() => setDocumentId(null)} />
      )}
    </Container>
  );
} 