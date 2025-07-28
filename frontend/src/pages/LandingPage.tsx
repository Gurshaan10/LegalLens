import { Container, Title, Text, Button, Group, Stack, rem } from '@mantine/core';
import { keyframes } from '@emotion/react';
import { motion } from 'framer-motion';
import { IconBrain, IconScale, IconLock } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';

const glowAnimation = keyframes({
  '0%': { textShadow: '0 0 10px rgba(171, 128, 73, 0)' },
  '50%': { textShadow: '0 0 20px rgba(171, 128, 73, 0.5)' },
  '100%': { textShadow: '0 0 10px rgba(171, 128, 73, 0)' },
});

const features = [
  {
    icon: IconBrain,
    title: 'AI-Powered Analysis',
    description: 'Advanced machine learning algorithms analyze your legal documents with precision and insight.'
  },
  {
    icon: IconScale,
    title: 'Legal Expertise',
    description: 'Trained on vast legal databases to provide accurate and relevant information.'
  },
  {
    icon: IconLock,
    title: 'Secure & Confidential',
    description: 'Enterprise-grade security ensures your documents remain private and protected.'
  }
];

const MotionGroup = motion.create(Group);
const MotionTitle = motion.create(Title);
const MotionText = motion.create(Text);

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <Container size="lg" py={100}>
      <Stack align="center" gap={50}>
        {/* Hero Section */}
        <Stack align="center" gap="xs">
          <MotionTitle
            order={1}
            size={rem(72)}
            c="bronze.3"
            ta="center"
            style={{ 
              animation: `${glowAnimation} 3s infinite`,
              fontWeight: 900,
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            Legal Lens
          </MotionTitle>
          <MotionText
            c="bronze.4"
            size="xl"
            ta="center"
            maw={600}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            Transform the way you analyze legal documents with AI-powered intelligence
          </MotionText>
          <MotionGroup
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            <Button
              size="lg"
              color="bronze"
              variant="filled"
              onClick={() => navigate('/login')}
              style={{
                background: 'linear-gradient(45deg, var(--mantine-color-bronze-8) 0%, var(--mantine-color-bronze-5) 100%)',
              }}
            >
              Get Started
            </Button>
            <Button
              size="lg"
              variant="outline"
              color="bronze"
              onClick={() => navigate('/about')}
            >
              Learn More
            </Button>
          </MotionGroup>
        </Stack>

        {/* Features Section */}
        <MotionGroup 
          justify="center" 
          gap={50}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9, duration: 0.8 }}
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2 + index * 0.2, duration: 0.8 }}
            >
              <Stack
                align="center"
                style={{
                  width: rem(300),
                  padding: rem(20),
                  backgroundColor: 'var(--mantine-color-dark-7)',
                  borderRadius: 'var(--mantine-radius-md)',
                  border: '1px solid var(--mantine-color-bronze-3)',
                }}
              >
                <feature.icon size={48} style={{ color: 'var(--mantine-color-bronze-4)' }} />
                <Title order={3} c="bronze.3">
                  {feature.title}
                </Title>
                <Text c="bronze.5" ta="center">
                  {feature.description}
                </Text>
              </Stack>
            </motion.div>
          ))}
        </MotionGroup>
      </Stack>
    </Container>
  );
} 