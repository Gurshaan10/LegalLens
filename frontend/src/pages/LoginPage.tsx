import { Container, Title, Text, Button, Paper, Stack, Group, Divider, TextInput, PasswordInput, Loader } from '@mantine/core';
import { motion } from 'framer-motion';
import { IconBrandGoogle } from '@tabler/icons-react';
import { signInWithPopup, signInWithEmailAndPassword, createUserWithEmailAndPassword, sendEmailVerification } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import { useNavigate } from 'react-router-dom';
import { notifications } from '@mantine/notifications';
import { useState } from 'react';

const MotionPaper = motion.create(Paper);

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true); // true = login, false = sign up
  const [loading, setLoading] = useState(false);
  const [verificationSent, setVerificationSent] = useState(false);
  const [unverifiedUser, setUnverifiedUser] = useState<any>(null);

  // Password validation regex: min 8 chars, 1 uppercase, 1 number, 1 special char
  const passwordRequirements = {
    regex: /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]).{8,}$/,
    message: 'Password must be at least 8 characters, include one uppercase letter, one number, and one special character.'
  };
  const [passwordError, setPasswordError] = useState<string | null>(null);

  const handleGoogleSignIn = async () => {
    try {
      setLoading(true);
      const result = await signInWithPopup(auth, googleProvider);
      notifications.show({
        title: 'Welcome!',
        message: 'Successfully signed in with Google',
        color: 'green'
      });
      navigate('/app/analysis');
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to sign in with Google. Please try again.',
        color: 'red'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);
    if (!passwordRequirements.regex.test(password)) {
      setPasswordError(passwordRequirements.message);
      return;
    }
    setLoading(true);
    try {
      if (isLogin) {
        const result = await signInWithEmailAndPassword(auth, email, password);
        if (!result.user.emailVerified) {
          setUnverifiedUser(result.user);
          notifications.show({
            title: 'Email not verified',
            message: 'Please verify your email before logging in.',
            color: 'yellow',
          });
          await auth.signOut();
          setLoading(false);
          return;
        }
        notifications.show({ title: 'Welcome!', message: 'Logged in successfully', color: 'green' });
        navigate('/app/analysis');
      } else {
        const result = await createUserWithEmailAndPassword(auth, email, password);
        await sendEmailVerification(result.user);
        setVerificationSent(true);
        notifications.show({
          title: 'Verify your email',
          message: 'A verification link has been sent to your email. Please verify before logging in.',
          color: 'blue',
        });
        await auth.signOut();
      }
    } catch (error: any) {
      notifications.show({
        title: 'Error',
        message: error.message || 'Authentication failed',
        color: 'red'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleResendVerification = async () => {
    if (unverifiedUser) {
      setLoading(true);
      try {
        await sendEmailVerification(unverifiedUser);
        notifications.show({
          title: 'Verification email sent',
          message: 'Check your inbox for a new verification link.',
          color: 'blue',
        });
      } catch (error: any) {
        notifications.show({
          title: 'Error',
          message: error.message || 'Failed to resend verification email',
          color: 'red',
        });
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <Container size={420} py={40}>
      <MotionPaper
        radius="md"
        p="xl"
        withBorder
        bg="dark.7"
        style={{ borderColor: 'var(--mantine-color-bronze-3)' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Stack gap="lg">
          <Title order={2} c="bronze.3" ta="center">
            Welcome to Legal Lens
          </Title>
          <Text c="bronze.5" size="sm" ta="center">
            Sign in to start analyzing your legal documents
          </Text>

          {verificationSent && (
            <Text c="bronze.4" ta="center">
              A verification link has been sent to <b>{email}</b>.<br />
              Please verify your email before logging in.
            </Text>
          )}

          {unverifiedUser && (
            <Stack gap="xs" align="center">
              <Text c="bronze.4" ta="center">
                Your email is not verified.<br />
                Please check your inbox and verify your email before logging in.
              </Text>
              <Button
                color="bronze"
                variant="outline"
                onClick={handleResendVerification}
                loading={loading}
              >
                Resend Verification Email
              </Button>
            </Stack>
          )}

          {!verificationSent && !unverifiedUser && (
            <>
              <Button
                leftSection={<IconBrandGoogle size={20} />}
                variant="default"
                color="gray"
                fullWidth
                onClick={handleGoogleSignIn}
                loading={loading}
              >
                Continue with Google
              </Button>

              <Divider label="or" labelPosition="center" />

              <form onSubmit={handleEmailAuth}>
                <Stack gap="sm">
                  <TextInput
                    label="Email"
                    placeholder="you@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.currentTarget.value)}
                    required
                    autoComplete="email"
                    disabled={loading}
                  />
                  <PasswordInput
                    label="Password"
                    placeholder="Your password"
                    value={password}
                    onChange={(e) => setPassword(e.currentTarget.value)}
                    required
                    autoComplete={isLogin ? 'current-password' : 'new-password'}
                    disabled={loading}
                    error={passwordError}
                  />
                  <Button
                    type="submit"
                    color="bronze"
                    fullWidth
                    loading={loading}
                  >
                    {isLogin ? 'Login with Email' : 'Sign Up with Email'}
                  </Button>
                  <Group justify="center">
                    <Text c="bronze.5" size="sm">
                      {isLogin ? "Don't have an account?" : 'Already have an account?'}
                      <Button
                        variant="subtle"
                        color="bronze"
                        size="xs"
                        onClick={() => setIsLogin((v) => !v)}
                        disabled={loading}
                        style={{ marginLeft: 8 }}
                      >
                        {isLogin ? 'Sign Up' : 'Login'}
                      </Button>
                    </Text>
                  </Group>
                </Stack>
              </form>
            </>
          )}

          <Divider />

          <Group grow>
            <Button
              variant="outline"
              color="bronze"
              onClick={() => navigate('/')}
              disabled={loading}
            >
              Back to Home
            </Button>
          </Group>
          {loading && <Loader color="bronze" />}
        </Stack>
      </MotionPaper>
    </Container>
  );
} 