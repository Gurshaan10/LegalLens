import { useState, useEffect } from 'react';
import { Dropzone } from '@mantine/dropzone';
import { Text, Group, rem, Button, useMantineTheme, Modal, Stack } from '@mantine/core';
import { IconUpload, IconX, IconFile } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { useAuth } from '../contexts/AuthContext';
import apiEndpoints from '../config/api';
import type { UploadResponse } from '../types/api';

interface DocumentUploadProps {
  onUploadSuccess: (filename: string) => void;
  credits?: number;
  isGuest?: boolean;
}

export default function DocumentUpload({ onUploadSuccess, credits, isGuest = false }: DocumentUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [guestUploadsRemaining, setGuestUploadsRemaining] = useState(() => {
    // Initialize from localStorage for guest users
    if (!isGuest) return 2;

    const stored = localStorage.getItem('guest_uploads_remaining');
    const date = localStorage.getItem('guest_uploads_date');
    const today = new Date().toDateString();

    // Reset counter if it's a new day
    if (date === today && stored) {
      return parseInt(stored, 10);
    }
    return 2;
  });
  const theme = useMantineTheme();
  const { getIdToken, user } = useAuth();

  // Update localStorage whenever guest uploads remaining changes
  useEffect(() => {
    if (isGuest) {
      localStorage.setItem('guest_uploads_remaining', String(guestUploadsRemaining));
      localStorage.setItem('guest_uploads_date', new Date().toDateString());
    }
  }, [guestUploadsRemaining, isGuest]);

  const handleDrop = async (files: File[]) => {
    if (files.length === 0) return;

    // Check credits for authenticated users
    if (!isGuest && credits === 0) {
      notifications.show({
        title: 'No Credits',
        message: 'You have no credits left. Please sign in or upgrade for more uploads.',
        color: 'red',
      });
      return;
    }

    // Check guest upload limit
    if (isGuest && guestUploadsRemaining <= 0) {
      notifications.show({
        title: 'Daily Limit Reached',
        message: 'You\'ve reached the daily limit for guest uploads (2 per day). Sign in to get 5 credits!',
        color: 'orange',
        autoClose: 5000,
      });
      return;
    }

    const file = files[0];
    console.log('Uploading file:', file.name, 'Size:', file.size);

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      notifications.show({
        title: 'Error',
        message: 'Please upload a PDF file',
        color: 'red',
      });
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Sending request to upload endpoint...');
      const headers: Record<string, string> = {};

      // Add authorization header only if user is authenticated
      if (!isGuest && user) {
        const idToken = await getIdToken();
        if (idToken) {
          headers['Authorization'] = `Bearer ${idToken}`;
        }
      }

      const response = await fetch(apiEndpoints.upload, {
        method: 'POST',
        body: formData,
        headers,
      });

      console.log('Response status:', response.status);
      const data: UploadResponse = await response.json();
      console.log('Response data:', data);

      if (!response.ok) {
        // Handle rate limit error specifically
        if (response.status === 429) {
          if (isGuest) {
            setGuestUploadsRemaining(0);
          }
          notifications.show({
            title: 'Daily Limit Reached',
            message: data.detail || 'You\'ve reached your daily upload limit. Sign in to get more credits!',
            color: 'orange',
            autoClose: 7000,
          });
          return;
        }
        throw new Error(data.detail || 'Upload failed');
      }

      // Update remaining uploads for guest users
      let newRemainingCount = guestUploadsRemaining;
      if (isGuest && data.is_guest) {
        newRemainingCount = Math.max(0, guestUploadsRemaining - 1);
        setGuestUploadsRemaining(newRemainingCount);
      }

      // Call success callback to open chat interface
      onUploadSuccess(data.document_id);

      const successMessage = isGuest
        ? `Document uploaded! ${newRemainingCount} guest upload(s) remaining today.`
        : `Document uploaded successfully! ${data.credits_remaining || 0} credit(s) remaining.`;

      notifications.show({
        title: 'Success',
        message: successMessage,
        color: 'bronze',
        autoClose: 5000,
      });
    } catch (error) {
      console.error('Upload error:', error);
      notifications.show({
        title: 'Error',
        message: error instanceof Error ? error.message : 'Failed to upload document. Please try again.',
        color: 'red',
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <>
      <Dropzone
        onDrop={handleDrop}
        maxSize={5 * 1024 ** 2}
        accept={['application/pdf']}
        loading={isUploading || (!isGuest && credits === 0) || (isGuest && guestUploadsRemaining === 0)}
        disabled={(!isGuest && credits === 0) || (isGuest && guestUploadsRemaining === 0)}
        style={{
          borderColor: theme.colors.bronze[3],
          backgroundColor: theme.colors.dark[7]
        }}
      >
        <Group justify="center" gap="xl" mih={220} style={{ pointerEvents: 'none' }}>
          <Dropzone.Accept>
            <IconUpload
              size={48}
              style={{
                color: theme.colors.bronze[4],
              }}
              stroke={1.5}
            />
          </Dropzone.Accept>
          <Dropzone.Reject>
            <IconX
              size={48}
              style={{
                color: theme.colors.red[6],
              }}
              stroke={1.5}
            />
          </Dropzone.Reject>
          <Dropzone.Idle>
            <IconFile
              size={48}
              style={{
                color: theme.colors.bronze[3],
              }}
              stroke={1.5}
            />
          </Dropzone.Idle>

          <div>
            <Text size="xl" inline c="bronze.3">
              Drag a PDF here or click to select
            </Text>
            <Text size="sm" c="bronze.5" inline mt={7}>
              File should not exceed 5MB
            </Text>
            {isGuest && (
              <Text size="sm" c="bronze.4" mt={7} fw={500}>
                Guest Mode: {guestUploadsRemaining} free upload{guestUploadsRemaining !== 1 ? 's' : ''} remaining today
              </Text>
            )}
            {!isGuest && credits === 0 && (
              <Text size="sm" c="red.5" mt={7}>
                You have no credits left. Please upgrade or contact support.
              </Text>
            )}
            {isGuest && guestUploadsRemaining === 0 && (
              <Text size="sm" c="orange.5" mt={7}>
                Daily limit reached. Sign in to get 5 credits!
              </Text>
            )}
          </div>
        </Group>
      </Dropzone>

      {/* Animated Lens Overlay */}
      {isUploading && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: '#1a1a1a',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 9999,
          }}
        >
          <Stack align="center" gap="xl">
            {/* Magnifying Glass */}
            <div
              style={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                animation: 'float 3s ease-in-out infinite',
              }}
            >
              {/* Lens Glass */}
              <div
                style={{
                  width: '100px',
                  height: '100px',
                  borderRadius: '50%',
                  background: `radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.3) 30%, rgba(255, 215, 0, 0.2) 60%, rgba(255, 165, 0, 0.1) 100%)`,
                  border: `3px solid ${theme.colors.bronze[4]}`,
                  position: 'relative',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  boxShadow: `
                    inset 0 0 20px rgba(255, 255, 255, 0.3),
                    0 0 30px ${theme.colors.bronze[4]},
                    0 0 50px rgba(255, 215, 0, 0.3)
                  `,
                  animation: 'lens 4s linear infinite',
                }}
              >
                {/* Lens Reflection */}
                <div
                  style={{
                    width: '30px',
                    height: '30px',
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.2) 100%)',
                    position: 'absolute',
                    top: '15px',
                    left: '15px',
                  }}
                />
                
                {/* Magnified Area Effect */}
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(255, 215, 0, 0.3) 0%, transparent 70%)',
                    position: 'absolute',
                    top: '30px',
                    left: '30px',
                    animation: 'magnify 2s ease-in-out infinite',
                  }}
                />
              </div>
              
              {/* Handle */}
              <div
                style={{
                  width: '8px',
                  height: '60px',
                  background: `linear-gradient(to bottom, ${theme.colors.bronze[4]} 0%, ${theme.colors.bronze[6]} 50%, ${theme.colors.bronze[8]} 100%)`,
                  borderRadius: '4px',
                  marginTop: '-5px',
                  boxShadow: `0 0 10px ${theme.colors.bronze[4]}`,
                }}
              />
              
              {/* Handle Grip */}
              <div
                style={{
                  width: '20px',
                  height: '15px',
                  background: `linear-gradient(to bottom, ${theme.colors.bronze[3]} 0%, ${theme.colors.bronze[5]} 100%)`,
                  borderRadius: '10px',
                  marginTop: '5px',
                  boxShadow: `0 0 8px ${theme.colors.bronze[3]}`,
                }}
              />
            </div>
            
            <Text size="lg" c="bronze.3" fw={500} ta="center">
              Analyzing Document
            </Text>
            <Text size="sm" c="bronze.5" ta="center">
              Please wait while we process your legal document...
            </Text>
          </Stack>
        </div>
      )}

      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes float {
            0%, 100% { 
              transform: translateY(0px);
            }
            50% { 
              transform: translateY(-10px);
            }
          }
          
          @keyframes lens {
            0% { 
              transform: rotate(0deg);
            }
            100% { 
              transform: rotate(360deg);
            }
          }
          
          @keyframes magnify {
            0%, 100% { 
              transform: scale(1);
              opacity: 0.5;
            }
            50% { 
              transform: scale(1.2);
              opacity: 0.8;
            }
          }
        `
      }} />
    </>
  );
} 